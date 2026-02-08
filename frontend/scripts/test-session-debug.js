/**
 * Debug script to test Better Auth session reading
 * Run with: node test-session-debug.js
 */

const { Pool } = require('pg');

// Load environment variables
require('dotenv').config({ path: '.env.local' });

async function testSessionDebug() {
  console.log('🔍 Better Auth Session Debug\n');

  // Check environment variables
  console.log('1. Environment Variables:');
  console.log('   BETTER_AUTH_URL:', process.env.BETTER_AUTH_URL || '❌ NOT SET');
  console.log('   NEXT_PUBLIC_BETTER_AUTH_URL:', process.env.NEXT_PUBLIC_BETTER_AUTH_URL || '❌ NOT SET');
  console.log('   BETTER_AUTH_SECRET:', process.env.BETTER_AUTH_SECRET ? `✅ Set (${process.env.BETTER_AUTH_SECRET.length} chars)` : '❌ NOT SET');
  console.log('   DATABASE_URL:', process.env.DATABASE_URL ? '✅ Set' : '❌ NOT SET');
  console.log();

  // Test database connection
  console.log('2. Testing Database Connection:');
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    connectionTimeoutMillis: 10000,
  });

  try {
    const client = await pool.connect();
    console.log('   ✅ Database connection successful');

    // Check if Better Auth tables exist
    const tablesResult = await client.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      AND table_name IN ('user', 'session', 'account', 'verification')
      ORDER BY table_name
    `);

    console.log('\n3. Better Auth Tables:');
    if (tablesResult.rows.length === 0) {
      console.log('   ❌ No Better Auth tables found!');
    } else {
      tablesResult.rows.forEach(row => {
        console.log(`   ✅ ${row.table_name}`);
      });
    }

    // Check for users
    const userCount = await client.query('SELECT COUNT(*) FROM "user"');
    console.log(`\n4. Users in Database: ${userCount.rows[0].count}`);

    // Check for sessions
    const sessionCount = await client.query('SELECT COUNT(*) FROM "session"');
    console.log(`5. Active Sessions: ${sessionCount.rows[0].count}`);

    if (parseInt(sessionCount.rows[0].count) > 0) {
      const sessions = await client.query(`
        SELECT
          s.id,
          s."userId",
          s."expiresAt",
          s."createdAt",
          u.email
        FROM "session" s
        JOIN "user" u ON s."userId" = u.id
        ORDER BY s."createdAt" DESC
        LIMIT 5
      `);

      console.log('\n6. Recent Sessions:');
      sessions.rows.forEach((s, i) => {
        const expired = new Date(s.expiresAt) < new Date();
        console.log(`   ${i + 1}. User: ${s.email}`);
        console.log(`      Session ID: ${s.id.substring(0, 20)}...`);
        console.log(`      Expires: ${s.expiresAt} ${expired ? '❌ EXPIRED' : '✅ Valid'}`);
        console.log(`      Created: ${s.createdAt}`);
      });
    }

    client.release();
    await pool.end();

    console.log('\n✅ Debug complete!');
    console.log('\n💡 Next Steps:');
    console.log('   1. Check if BETTER_AUTH_URL is set (both with and without NEXT_PUBLIC)');
    console.log('   2. Verify sessions exist and are not expired');
    console.log('   3. Check browser DevTools → Application → Cookies for "session" cookie');
    console.log('   4. Compare cookie value with session token in database');

  } catch (error) {
    console.error('   ❌ Error:', error.message);
    await pool.end();
  }
}

testSessionDebug().catch(console.error);
