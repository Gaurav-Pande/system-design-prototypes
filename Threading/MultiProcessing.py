#
# Small Prototype to learn multithreading
# A function ==> count prime number
# 
import math
import argparse
import time
import multiprocessing
import sys

class CountPrimes:
    def __init__(self, maxlimit):
        """ Initial variables, only used for non threaded workflow"""
        self.countUntil = maxlimit
        self.numberOfPrimes = 0

    def countPrimesRange(self, start, end, result, executiontime):
        """For a threaded workflow count the primes and add them to thread safe queue"""
        res = 0
        startTime = time.time()
        for num in range(start, end+1):
            if self.isPrime(num):
                res+=1
        endTime = time.time()
        result.put(res)
        executiontime.put(endTime-startTime)

    def countPrimes(self):
        """Method for counting prime for non threaded workflow"""
        for num in range(2, self.countUntil+1):
            if self.isPrime(num):
                self.numberOfPrimes+=1
        
    def isPrime(self, num):
        """Helper method to check if a number is prime"""
        if num <= 1:
            return False
        for div in range(2, int(math.sqrt(num))+1):
            if num% div==0:
                return False
        return True
    

def main():
    parser = argparse.ArgumentParser(description="Multi threading example")
    parser.add_argument('-c', '--countUntil', type=int, default=10, 
                        help='Count number of prime until (default: 10)')
    parser.add_argument('-t', '--processCount', type=int, default =1,
                        help='Number of threads to spawn for calculation (default: 1)')
    parser.add_argument('-f', '--flag', type=bool, default=False,
                        help= 'Flag to turn multi threading on/off ( default: Flase)')
    args = parser.parse_args()
    
    cli = CountPrimes(args.countUntil)
    
    if not args.flag:
        startTime = time.time()
        cli.countPrimes()
        endTime = time.time()
        print(f" Total number of primes until: {args.countUntil} are: {cli.numberOfPrimes}")
        print(f"Time took to calculate: {endTime-startTime} seconds")
    else:

        chunks = args.countUntil // args.processCount
        remaining = args.countUntil % args.processCount

        processes = []
        resultList = multiprocessing.Queue()
        threadExecutionTime = multiprocessing.Queue()

        for i in range(args.processCount):
            start = i*chunks +1
            if i < args.processCount -1:
                end = (i+1)*chunks
            else:
                end = args.countUntil

            # add the remaining to the last thread.
            if i == args.processCount-1:
                end+= remaining

            process = multiprocessing.Process(target = cli.countPrimesRange, args=(start, end, resultList, threadExecutionTime))   
            processes.append(process)
            process.start()


            for process in processes:
                process.join()

            for process in processes:
                if process.is_alive():
                    process.terminate()
        
            print(f" Total number of primes from start : {start} to end: {end}  are: {resultList.get()}, Time took : {threadExecutionTime.get()}")
        print(f"Sum of all primes are: {sum(resultList.get() for _ in range(args.processCount))} Total time took: {sum(threadExecutionTime.get() for _ in range(args.processCount))}")
        sys.exit(0)
    

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn') 
    main()


            
