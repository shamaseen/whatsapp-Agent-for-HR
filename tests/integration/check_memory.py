#!/usr/bin/env python3
"""
Check memory checkpoints in database
"""
import psycopg
from config import settings

def check_checkpoints():
    """Check all checkpoints in database"""
    conn = psycopg.connect(settings.DATABASE_URL)

    print("="*80)
    print("CHECKPOINT MEMORY STATUS")
    print("="*80 + "\n")

    # Check if tables exist
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('checkpoints', 'checkpoint_writes')
        """)
        tables = [row[0] for row in cur.fetchall()]

        print("Tables:")
        for table in tables:
            print(f"  ✅ {table}")

        if 'checkpoints' not in tables:
            print("\n❌ checkpoints table does not exist!")
            print("   Run the application once to create it.")
            return

    # Count total checkpoints
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM checkpoints")
        total = cur.fetchone()[0]
        print(f"\nTotal checkpoints: {total}")

    # List all thread_ids
    with conn.cursor() as cur:
        cur.execute("""
            SELECT thread_id, COUNT(*) as checkpoint_count
            FROM checkpoints
            GROUP BY thread_id
            ORDER BY MAX(checkpoint_id) DESC
        """)

        results = cur.fetchall()

        if results:
            print(f"\nConversations ({len(results)} users):")
            print("-"*80)
            for thread_id, count in results:
                print(f"  Thread ID: {thread_id}")
                print(f"  Checkpoints: {count}")
                print()
        else:
            print("\n⚠️  No checkpoints found in database")
            print("   Send a message to create the first checkpoint")

    # Show last 5 checkpoints
    with conn.cursor() as cur:
        cur.execute("""
            SELECT thread_id, checkpoint_id, type
            FROM checkpoints
            ORDER BY checkpoint_id DESC
            LIMIT 5
        """)

        results = cur.fetchall()

        if results:
            print("\nRecent checkpoints:")
            print("-"*80)
            for thread_id, checkpoint_id, checkpoint_type in results:
                print(f"  Thread: {thread_id}")
                print(f"  Checkpoint ID: {checkpoint_id}")
                print(f"  Type: {checkpoint_type}")
                print()

    conn.close()

    print("="*80)
    print("\nTo check specific user:")
    print("  python3 check_memory.py 962778435754")
    print()

def check_specific_thread(thread_id):
    """Check checkpoints for specific thread"""
    conn = psycopg.connect(settings.DATABASE_URL)

    print("="*80)
    print(f"CHECKPOINTS FOR: {thread_id}")
    print("="*80 + "\n")

    with conn.cursor() as cur:
        cur.execute("""
            SELECT checkpoint_id, type, parent_checkpoint_id
            FROM checkpoints
            WHERE thread_id = %s
            ORDER BY checkpoint_id
        """, (thread_id,))

        results = cur.fetchall()

        if results:
            print(f"Found {len(results)} checkpoints:\n")
            for i, (cp_id, cp_type, parent_id) in enumerate(results, 1):
                print(f"{i}. Checkpoint: {cp_id}")
                print(f"   Type: {cp_type}")
                print(f"   Parent: {parent_id}")
                print()
        else:
            print(f"❌ No checkpoints found for thread_id: {thread_id}")
            print("\nPossible reasons:")
            print("  1. User hasn't sent any messages yet")
            print("  2. Different thread_id format (check phone number)")
            print("  3. Checkpointer not saving properly")

            # Show similar thread_ids
            cur.execute("""
                SELECT DISTINCT thread_id
                FROM checkpoints
                WHERE thread_id LIKE %s
                LIMIT 5
            """, (f"%{thread_id[-5:]}%",))

            similar = cur.fetchall()
            if similar:
                print("\n  Similar thread_ids found:")
                for (tid,) in similar:
                    print(f"    - {tid}")

    conn.close()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        thread_id = sys.argv[1]
        check_specific_thread(thread_id)
    else:
        check_checkpoints()
