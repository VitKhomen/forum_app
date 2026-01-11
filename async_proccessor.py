import asyncio
import random


class AsyncProcessor:

    def __init__(self, items, workers=3):
        self.items_count = items
        self.workers_count = workers
        self.raw_data_queue = asyncio.Queue()
        self.processed_data_queue = asyncio.Queue()

    async def generate_data(self):
        for i in range(self.items_count):
            data = {'id': i, 'status': 'raw'}
            await asyncio.sleep(random.uniform(0, 0.5))
            print(f'[GEN] {data}')
            await self.raw_data_queue.put(data)

    async def process_data(self, w_id):
        while True:
            data = await self.raw_data_queue.get()
            await asyncio.sleep(random.uniform(0.1, 1.0))
            data['status'] = 'processed'
            print(f'[WORKER{w_id}] {data}')
            await self.processed_data_queue.put(data)

    async def aggregate_results(self):
        for _ in range(self.items_count):
            data = await self.processed_data_queue.get()
            print(f'[AGR] {data}')

    async def run(self):
        producers = [asyncio.create_task(self.generate_data())]
        workers = [asyncio.create_task(self.process_data(
            w_id)) for w_id in range(self.workers_count)]
        aggregator = asyncio.create_task(self.aggregate_results())

        await asyncio.gather(*producers)
        await self.raw_data_queue.join()

        for w in workers:
            w.cancel()

        await self.processed_data_queue.join()
        await aggregator


async def main():
    processor = AsyncProcessor(10)
    await processor.run()


if __name__ == '__main__':
    asyncio.run(main())
