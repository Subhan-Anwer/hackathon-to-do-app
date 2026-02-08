/**
 * Database Connection Test Script
 *
 * Tests if the Neon PostgreSQL database is accessible and responsive.
 * Run this before starting the app to verify database connectivity.
 */

const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

// Read .env.local manually
const envPath = path.join(__dirname, '.env.local');
const envContent = fs.readFileSync(envPath, 'utf8');
const DATABASE_URL = envContent.match(/DATABASE_URL=(.+)/)?.[1]?.trim();

if (!DATABASE_URL) {
  console.error('❌ DATABASE_URL not found in .env.local');
  process.exit(1);
}

const pool = new Pool({
  connectionString: DATABASE_URL,
  connectionTimeoutMillis: 20000,
  idleTimeoutMillis: 30000,
  max: 3,
  min: 0,
});

async function testConnection() {
  console.log('🔍 Testing Neon PostgreSQL connection...\n');
  console.log('Connection string:', DATABASE_URL.replace(/:[^:]*@/, ':****@'));
  console.log('');

  const startTime = Date.now();

  try {
    console.log('⏳ Attempting to connect (this may take 10-20 seconds for Neon wake-up)...');

    const client = await pool.connect();
    const connectionTime = ((Date.now() - startTime) / 1000).toFixed(2);

    console.log(`✅ Connected successfully in ${connectionTime}s`);
    console.log('');

    // Test query
    console.log('🔍 Running test query...');
    const result = await client.query('SELECT NOW() as current_time, version() as db_version');
    console.log('✅ Query successful:');
    console.log('   Current time:', result.rows[0].current_time);
    console.log('   PostgreSQL version:', result.rows[0].db_version.split(' ')[0] + ' ' + result.rows[0].db_version.split(' ')[1]);
    console.log('');

    // Check if Better Auth tables exist
    console.log('🔍 Checking Better Auth tables...');
    const tablesResult = await client.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      AND table_name IN ('user', 'session', 'account', 'verification')
      ORDER BY table_name
    `);

    if (tablesResult.rows.length > 0) {
      console.log('✅ Better Auth tables found:');
      tablesResult.rows.forEach(row => {
        console.log(`   - ${row.table_name}`);
      });
    } else {
      console.log('⚠️  No Better Auth tables found (will be created on first auth operation)');
    }
    console.log('');

    client.release();
    await pool.end();

    console.log('✅ Database connection test PASSED');
    console.log('');
    console.log('✅ Your Neon database is working correctly!');
    console.log('   You can now start the frontend: cd frontend && npm run dev');

    process.exit(0);
  } catch (error) {
    const errorTime = ((Date.now() - startTime) / 1000).toFixed(2);
    console.error(`❌ Connection failed after ${errorTime}s`);
    console.error('');
    console.error('Error details:');
    console.error('  Code:', error.code);
    console.error('  Message:', error.message);
    console.error('');

    if (error.code === 'ETIMEDOUT') {
      console.error('🔧 TROUBLESHOOTING:');
      console.error('');
      console.error('   1. Your Neon database may be sleeping (free tier)');
      console.error('      → Go to https://console.neon.tech');
      console.error('      → Find your project and click "Wake Database"');
      console.error('      → Wait 30 seconds and try again');
      console.error('');
      console.error('   2. Check your connection string in frontend/.env.local');
      console.error('      → Verify DATABASE_URL is correct');
      console.error('      → Should start with: postgresql://');
      console.error('');
      console.error('   3. Consider using local PostgreSQL for development:');
      console.error('      → docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres');
      console.error('      → Update DATABASE_URL to: postgresql://postgres:postgres@localhost:5432/todo_app');
    } else if (error.code === 'ENOTFOUND') {
      console.error('🔧 TROUBLESHOOTING:');
      console.error('   → Cannot resolve database hostname');
      console.error('   → Check your internet connection');
      console.error('   → Verify DATABASE_URL in frontend/.env.local');
    } else {
      console.error('🔧 TROUBLESHOOTING:');
      console.error('   → Check your DATABASE_URL in frontend/.env.local');
      console.error('   → Verify BETTER_AUTH_SECRET is set');
      console.error('   → Ensure firewall allows connections to Neon');
    }

    process.exit(1);
  }
}

testConnection();
