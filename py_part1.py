import py_cord as reference
import multiprocessing

if __name__ == '__main__':
    #SIMULATION1
    object = reference.Operations(2, 1,0)
    process1 = multiprocessing.Process(target=object.sender, args=( ))
    process2 = multiprocessing.Process(target=object.receiver, args=())
    process2.start()
    process1.start()
    process1.join(timeout=50)
    process2.join(timeout=50)
    process1.terminate()
    process2.terminate()

    #SIMULATION2

    object = reference.Operations(2, 2,1)
    process1 = multiprocessing.Process(target=object.sender, args=( ))
    process2 = multiprocessing.Process(target=object.receiver, args=())
    process2.start()
    process1.start()
    process1.join(timeout=50)
    process2.join(timeout=50)
    process1.terminate()
    process2.terminate()

    #SIMULATION3

    object = reference.Operations(2, 3, 1)
    process1 = multiprocessing.Process(target=object.sender, args=( ))
    process2 = multiprocessing.Process(target=object.receiver, args=())
    process2.start()
    process1.start()
    process1.join(timeout=80)
    process2.join(timeout=80)
    process1.terminate()
    process2.terminate()


    #SIMULATION4

    object = reference.Operations(2, 4, 2)
    process1 = multiprocessing.Process(target=object.sender, args=( ))
    process2 = multiprocessing.Process(target=object.receiver, args=())
    process2.start()
    process1.start()
    process1.join(timeout=90)
    process2.join(timeout=90)
    process1.terminate()
    process2.terminate()

