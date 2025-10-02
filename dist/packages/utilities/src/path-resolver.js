import path from "path";
export class PathResolver {
    aliases = new Map();
    constructor(initialAliases = []) {
        initialAliases.forEach(({ alias, target }) => this.registerAlias(alias, target));
    }
    registerAlias(alias, target) {
        if (!alias) {
            throw new Error("Alias cannot be empty.");
        }
        const normalizedAlias = alias.endsWith("/") ? alias.slice(0, -1) : alias;
        const normalizedTarget = this.normalize(target);
        this.aliases.set(normalizedAlias, normalizedTarget);
    }
    hasAlias(alias) {
        return this.aliases.has(alias);
    }
    resolve(importPath, fromPath) {
        if (!importPath) {
            throw new Error("Import path cannot be empty.");
        }
        const aliasMatch = this.findAlias(importPath);
        if (aliasMatch) {
            const suffix = importPath.substring(aliasMatch.alias.length);
            return this.normalize(path.join(aliasMatch.target, suffix));
        }
        if (importPath.startsWith(".") && fromPath) {
            const baseDir = path.dirname(fromPath);
            return this.normalize(path.resolve(baseDir, importPath));
        }
        return this.normalize(importPath);
    }
    clear() {
        this.aliases.clear();
    }
    findAlias(importPath) {
        const entries = Array.from(this.aliases.entries()).sort((a, b) => b[0].length - a[0].length);
        for (const [alias, target] of entries) {
            if (importPath === alias || importPath.startsWith(alias + "/")) {
                return { alias, target };
            }
        }
        return undefined;
    }
    normalize(target) {
        const replaced = target.split("\\").join("/");
        return path.posix.normalize(replaced);
    }
}
export const defaultPathResolver = new PathResolver();
