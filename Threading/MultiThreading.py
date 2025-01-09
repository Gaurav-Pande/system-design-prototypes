#
# Small Prototype to learn multithreading
# A function ==> count prime number
# 
import math
import argparse
import time
import threading

class CountPrimes:
    def __init__(self, maxlimit):
        """ Initial variables, only used for non threaded workflow"""
        self.countUntil = maxlimit
        self.numberOfPrimes = 0

    def countPrimesRange(self, start, end, result, executiontime, lock):
        """For a threaded workflow count the primes and add them to thread safe queue"""
        res = 0
        startTime = time.time()
        for num in range(start, end+1):
            if self.isPrime(num):
                res+=1
        endTime = time.time()
        with lock:
            result.append(res)
            executiontime.append(endTime-startTime)

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
    parser.add_argument('-t', '--threadCount', type=int, default =1,
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

        chunks = args.countUntil // args.threadCount
        remaining = args.countUntil % args.threadCount

        threads = []
        threadLock = threading.Lock()
        resultList = []
        threadExecutionTime = []

        for i in range(args.threadCount):
            start = i*chunks +1
            if i < args.threadCount -1:
                end = (i+1)*chunks
            else:
                end = args.countUntil

            # add the remaining to the last thread.
            if i == args.threadCount-1:
                end+= remaining

            thread = threading.Thread(target = cli.countPrimesRange, args=(start, end, resultList, threadExecutionTime, threadLock))   
            threads.append(thread)
            thread.start()


            for thread in threads:
                thread.join()
        
            print(f" Total number of primes from start : {start} to end: {end}  are: {resultList[i]}, Time took : {threadExecutionTime[i]}")
        print(f"Sum of all primes are: {sum(resultList)} Total time took: {sum(threadExecutionTime)}")
        
    

if __name__ == "__main__":
    main()


            
