#!/usr/bin/env node

/**
 * Lint Regression Testing Suite
 *
 * This script runs comprehensive lint checks and compares results
 * against baseline metrics to detect regressions.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class LintRegressionTester {
  constructor() {
    this.baselineFile = 'baseline_metrics.txt';
    this.resultsDir = 'lint-regression-results';
    this.currentResults = null;
  }

  /**
   * Run comprehensive lint check
   */
  runLintCheck() {
    console.log('🔍 Running comprehensive lint check...');

    try {
      const output = execSync('./check_lint_all.ps1', {
        encoding: 'utf8',
        maxBuffer: 1024 * 1024 * 10 // 10MB buffer
      });

      this.currentResults = this.parseLintOutput(output);
      return this.currentResults;
    } catch (error) {
      console.error('❌ Failed to run lint check:', error.message);
      throw error;
    }
  }

  /**
   * Parse lint output into structured data
   */
  parseLintOutput(output) {
    const lines = output.split('\n');
    const results = {
      timestamp: new Date().toISOString(),
      domains: {},
      summary: {
        totalDomains: 0,
        cleanDomains: 0,
        errorDomains: 0,
        totalErrors: 0,
        totalWarnings: 0
      }
    };

    let currentDomain = null;

    for (const line of lines) {
      const trimmed = line.trim();

      // Check for domain status lines
      if (trimmed.includes('is clean')) {
        const domainMatch = trimmed.match(/^(.+?) is clean$/);
        if (domainMatch) {
          currentDomain = domainMatch[1];
          results.domains[currentDomain] = {
            status: 'clean',
            errors: 0,
            warnings: 0
          };
          results.summary.cleanDomains++;
        }
      } else if (trimmed.includes('has lint errors')) {
        const domainMatch = trimmed.match(/^(.+?) has lint errors$/);
        if (domainMatch) {
          currentDomain = domainMatch[1];
          results.domains[currentDomain] = {
            status: 'errors',
            errors: 0,
            warnings: 0
          };
          results.summary.errorDomains++;
        }
      }
    }

    results.summary.totalDomains = Object.keys(results.domains).length;

    return results;
  }

  /**
   * Load baseline metrics
   */
  loadBaseline() {
    try {
      if (!fs.existsSync(this.baselineFile)) {
        console.warn(`⚠️  Baseline file ${this.baselineFile} not found`);
        return null;
      }

      const content = fs.readFileSync(this.baselineFile, 'utf8');
      return this.parseLintOutput(content);
    } catch (error) {
      console.error('❌ Failed to load baseline:', error.message);
      return null;
    }
  }

  /**
   * Compare current results with baseline
   */
  compareWithBaseline(current, baseline) {
    if (!baseline) {
      console.log('📊 No baseline available for comparison');
      return null;
    }

    const comparison = {
      regressions: [],
      improvements: [],
      newDomains: [],
      removedDomains: [],
      summary: {
        baselineClean: baseline.summary.cleanDomains,
        currentClean: current.summary.cleanDomains,
        cleanChange: current.summary.cleanDomains - baseline.summary.cleanDomains
      }
    };

    // Compare domain statuses
    for (const [domain, currentStatus] of Object.entries(current.domains)) {
      const baselineStatus = baseline.domains[domain];

      if (!baselineStatus) {
        comparison.newDomains.push(domain);
      } else if (baselineStatus.status === 'clean' && currentStatus.status !== 'clean') {
        comparison.regressions.push({
          domain,
          from: baselineStatus.status,
          to: currentStatus.status
        });
      } else if (baselineStatus.status !== 'clean' && currentStatus.status === 'clean') {
        comparison.improvements.push({
          domain,
          from: baselineStatus.status,
          to: currentStatus.status
        });
      }
    }

    // Check for removed domains
    for (const domain of Object.keys(baseline.domains)) {
      if (!current.domains[domain]) {
        comparison.removedDomains.push(domain);
      }
    }

    return comparison;
  }

  /**
   * Generate regression report
   */
  generateReport(comparison) {
    const report = {
      timestamp: new Date().toISOString(),
      status: 'PASS',
      summary: comparison.summary,
      details: {}
    };

    if (comparison.regressions.length > 0) {
      report.status = 'FAIL';
      report.details.regressions = comparison.regressions;
    }

    if (comparison.improvements.length > 0) {
      report.details.improvements = comparison.improvements;
    }

    if (comparison.newDomains.length > 0) {
      report.details.newDomains = comparison.newDomains;
    }

    if (comparison.removedDomains.length > 0) {
      report.details.removedDomains = comparison.removedDomains;
    }

    return report;
  }

  /**
   * Save results to file
   */
  saveResults(results, filename) {
    if (!fs.existsSync(this.resultsDir)) {
      fs.mkdirSync(this.resultsDir, { recursive: true });
    }

    const filepath = path.join(this.resultsDir, filename);
    fs.writeFileSync(filepath, JSON.stringify(results, null, 2));
    console.log(`💾 Results saved to ${filepath}`);

    return filepath;
  }

  /**
   * Run the complete regression test
   */
  async run() {
    console.log('🚀 Starting Lint Regression Test Suite\n');

    try {
      // Run lint check
      const currentResults = this.runLintCheck();
      console.log(`✅ Lint check completed - ${currentResults.summary.cleanDomains}/${currentResults.summary.totalDomains} domains clean\n`);

      // Load baseline
      const baseline = this.loadBaseline();

      // Compare with baseline
      const comparison = this.compareWithBaseline(currentResults, baseline);

      if (comparison) {
        console.log('📊 Regression Analysis:');
        console.log(`   Clean domains: ${comparison.summary.baselineClean} → ${comparison.summary.currentClean} (${comparison.summary.cleanChange >= 0 ? '+' : ''}${comparison.summary.cleanChange})`);

        if (comparison.regressions.length > 0) {
          console.log(`   ❌ Regressions: ${comparison.regressions.length}`);
          comparison.regressions.forEach(r => console.log(`      - ${r.domain}: ${r.from} → ${r.to}`));
        }

        if (comparison.improvements.length > 0) {
          console.log(`   ✅ Improvements: ${comparison.improvements.length}`);
          comparison.improvements.forEach(i => console.log(`      - ${i.domain}: ${i.from} → ${i.to}`));
        }

        if (comparison.newDomains.length > 0) {
          console.log(`   🆕 New domains: ${comparison.newDomains.length}`);
          comparison.newDomains.forEach(d => console.log(`      - ${d}`));
        }
      }

      // Generate and save report
      const report = this.generateReport(comparison || { summary: currentResults.summary, regressions: [], improvements: [], newDomains: [], removedDomains: [] });
      const reportFile = this.saveResults(report, `regression-report-${Date.now()}.json`);

      // Final status
      console.log(`\n🏁 Test ${report.status === 'PASS' ? 'PASSED' : 'FAILED'}`);
      console.log(`📄 Full report: ${reportFile}`);

      if (report.status === 'FAIL') {
        console.log('\n❌ Regressions detected! Please fix before committing.');
        process.exit(1);
      } else {
        console.log('\n✅ No regressions detected. Ready to proceed.');
      }

    } catch (error) {
      console.error('💥 Regression test failed:', error.message);
      process.exit(1);
    }
  }
}

// Run the test suite
if (require.main === module) {
  const tester = new LintRegressionTester();
  tester.run().catch(console.error);
}

module.exports = LintRegressionTester;