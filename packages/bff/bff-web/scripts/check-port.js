#!/usr/bin/env node

/**
 * Utility script to check port availability and manage server processes
 * Usage:
 *   node scripts/check-port.js 4001  # Check if port 4001 is available
 *   node scripts/check-port.js       # Check default ports
 */

const { execSync } = require('child_process');

const portsToCheck = process.argv.length > 2 ? [process.argv[2]] : [4001, 3000, 8080];

console.log('🔍 Checking port availability...\n');

portsToCheck.forEach(port => {
  try {
    const output = execSync(`netstat -ano | findstr :${port}`, { encoding: 'utf8' });
    if (output.trim()) {
      console.log(`❌ Port ${port}: OCCUPIED`);
      const lines = output.trim().split('\n');
      lines.forEach(line => {
        const parts = line.trim().split(/\s+/);
        const pid = parts[parts.length - 1];
        if (pid && pid !== '0') {
          try {
            const processInfo = execSync(`tasklist /FI "PID eq ${pid}" /FO CSV /NH`, { encoding: 'utf8' });
            console.log(`   Process: ${processInfo.split(',')[0].replace(/"/g, '')} (PID: ${pid})`);
          } catch (e) {
            console.log(`   PID: ${pid}`);
          }
        }
      });
    } else {
      console.log(`✅ Port ${port}: Available`);
    }
  } catch (error) {
    console.log(`✅ Port ${port}: Available`);
  }
});

console.log('\n💡 Tips to manage port conflicts:');
console.log('   1. Use this script before starting servers');
console.log('   2. Set PORT environment variable to use different ports');
console.log('   3. Kill conflicting processes: taskkill /PID <PID> /F');
console.log('   4. Check all ports: netstat -ano | findstr LISTENING');