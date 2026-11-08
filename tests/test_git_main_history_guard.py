"""Actual Git reference transactions: preserve parallel history and existing hooks."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('main_history_installer',ROOT/'scripts/install_main_history_guard.py')
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
TEMPLATE=(ROOT/'.husky/reference-transaction').read_bytes()


class MainHistoryGuard(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='git-history-contract-')
        self.repo=Path(self.temp.name)/'repo';self.repo.mkdir()
        self.env={**os.environ,'GIT_AUTHOR_NAME':'Synthetic','GIT_AUTHOR_EMAIL':'fixture@example.invalid',
            'GIT_COMMITTER_NAME':'Synthetic','GIT_COMMITTER_EMAIL':'fixture@example.invalid'}
        for key in ['GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE']:
            self.env.pop(key,None)
        self.run_git('init','-q','--initial-branch=main')
        self.tree=self.run_git('mktree',input=b'').stdout.decode().strip()
        self.root=self.commit();self.run_git('update-ref','refs/heads/main',self.root)

    def tearDown(self):
        self.temp.cleanup()

    def run_git(self,*args,input=None,allowed=True,env=None):
        result=subprocess.run(['git','-C',str(self.repo),*args],input=input,capture_output=True,env=env or self.env)
        if allowed:self.assertEqual(result.returncode,0,result.stderr.decode())
        return result

    def commit(self,*parents):
        self.sequence=getattr(self,'sequence',0)+1
        args=['commit-tree',self.tree,'-m',f'synthetic {self.sequence}']
        for parent in parents:args+=['-p',parent]
        return self.run_git(*args).stdout.decode().strip()

    def test_forward_merge_and_feature_rewrite_work_but_main_rewind_and_divergence_fail(self):
        self.assertTrue(installer.install(self.repo,TEMPLATE))
        child=self.commit(self.root);sibling=self.commit(self.root)
        self.run_git('update-ref','refs/heads/main',child)
        for candidate in (self.root,sibling):
            self.assertNotEqual(self.run_git('update-ref','refs/heads/main',candidate,allowed=False).returncode,0)
            self.assertEqual(self.run_git('rev-parse','main').stdout.decode().strip(),child)
        merge=self.commit(child,sibling)
        self.run_git('update-ref','refs/heads/main',merge)
        self.assertNotEqual(self.run_git('update-ref','-d','refs/heads/main',allowed=False).returncode,0)
        self.run_git('update-ref','refs/heads/feature',child)
        self.run_git('update-ref','refs/heads/feature',sibling)

    def test_private_worktree_cannot_skip_guard_and_other_husky_hooks_survive(self):
        hooks=self.repo/'.husky'/'_';hooks.mkdir(parents=True)
        preserved=hooks/'pre-push';preserved.write_bytes(b'#!/bin/sh\nexit 0\n')
        self.run_git('config','core.hooksPath','.husky/_')
        self.assertTrue(installer.install(self.repo,TEMPLATE))
        self.assertEqual(preserved.read_bytes(),b'#!/bin/sh\nexit 0\n')
        private=Path(self.temp.name)/'private';private.mkdir()
        child=self.commit(self.root);self.run_git('update-ref','refs/heads/main',child)
        env={**self.env,'GIT_DIR':str(self.repo/'.git'),'GIT_WORK_TREE':str(private)}
        denied=self.run_git('update-ref','refs/heads/main',self.root,allowed=False,env=env)
        self.assertNotEqual(denied.returncode,0)
        self.assertTrue(installer.install(self.repo,TEMPLATE,check=True))

    def test_existing_foreign_hook_is_never_replaced(self):
        target=self.repo/'.git'/'hooks'/'reference-transaction';target.write_bytes(b'foreign hook')
        with self.assertRaises(RuntimeError):installer.install(self.repo,TEMPLATE)
        self.assertEqual(target.read_bytes(),b'foreign hook')
