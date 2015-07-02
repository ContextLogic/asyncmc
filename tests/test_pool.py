from time import sleep
from ._testutil import run_until_complete, BaseTest
from asyncmc.pool import ConnectionPool, Connection


class PoolTest(BaseTest):

    @run_until_complete
    def test_utils(self):
        sleep(1)
        self.assertEqual(0, 0)

    @run_until_complete
    def test_pool_creation(self):
        pool = ConnectionPool(['memcached:11211'], debug=1)
        self.assertEqual(pool.size(), 0)

    @run_until_complete
    def test_pool_acquire_release(self):
        pool = ConnectionPool(['memcached:11211'], debug=1)
        conn = yield pool.acquire()
        self.assertIsInstance(conn, Connection)
        pool.release(conn)

    @run_until_complete
    def test_pool_clear(self):
        pool = ConnectionPool(['memcached:11211'], debug=1)
        conn = yield pool.acquire()
        pool.release(conn)
        self.assertEqual(pool.size(), 1)
        yield pool.clear()
        self.assertEqual(pool._pool.qsize(), 0)

    @run_until_complete
    def test_pool_is_full(self):
        pool = ConnectionPool(
            ['memcached:11211'],
            minsize=1,
            maxsize=2,
            debug=1
        )
        conn = yield pool.acquire()

        # put garbage to the pool make it look like full
        mocked_conns = [Connection([]), Connection([])]
        yield pool._pool.put(mocked_conns[0])
        yield pool._pool.put(mocked_conns[1])

        # try to return connection back
        self.assertEqual(pool.size(), 3)
        pool.release(conn)
        self.assertEqual(pool.size(), 2)
