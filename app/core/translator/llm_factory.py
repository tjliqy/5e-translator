import threading
import time
# import queue
from collections import deque
from config import logger
from app.core.utils import TranslatorStatus


def done_f(obj):
    # print("DONE" + str(obj))
    pass


def all_done_f(obj):
    print(len(obj))
    # print("ALLDONE" + str(obj))


def more_job_f(jobs):
    return False


class LLMFactory:
    def __init__(
        self, work_num,
        work_func:callable,
        done_func=done_f,
        all_done_func=all_done_f
    ) -> (None):
        """生成llm的工厂类
        Args:
            work_num (int): 工作线程数
            work_func (function): 处理Job的函数
            done_func (function, optional): 单个job处理完成回调. Defaults to done_f.
            all_done_func (function, optional): 所有job处理完成回调. Defaults to all_done_f.
        """
        self.work_num = work_num
        self.work_func = work_func
        self.add_finish = False
        self.job_count = 0
        self.finish_count = 0
        self.job_queue = deque()
        self.done_func = done_func
        self.all_done_func = all_done_func
        self.res_obj = []
        self.lock = threading.Lock()
        self.workers = []

    def add_jobs(self, objs: list):
        self.lock.acquire()
        self.job_count += len(objs)
        for j in objs:
            self.job_queue.append(j)
        self.lock.release()

    def reset_job(self, job: list, add_err_num: bool = True):
        self.lock.acquire()
        if add_err_num:
            job.err_time += 1
        if job.err_time <= 3:
            self.job_queue.append(job)
        else:
            logger.error(f"解析JOB超过最大重试次数，跳过JOB：{job}")
        self.lock.release()

    def set_finish(self, add_finish):
        self.add_finish = add_finish

    def get_job(self):
        self.lock.acquire()
        if len(self.job_queue) != 0:
            j = self.job_queue.popleft()
            self.lock.release()
            return j
        else:
            self.lock.release()
            return None

    def done_job(self, job):
        self.lock.acquire()
        self.finish_count += 1
        self.res_obj.append(job)
        isF = self.isFinish()
        self.lock.release()

        self.done_func(job)
        if isF:
            self.all_done_func(self.res_obj)

    def isFinish(self):
        return (
            len(self.job_queue) == 0
            and self.add_finish
            and self.finish_count == self.job_count
        )

    def start_work(self):
        for i in range(self.work_num):
            self.workers.append(
                threading.Thread(target=kimi_work,
                                 args=(self, self.work_func,
                                       i,
                                       ))
            )
        for w in self.workers:
            w.start()
        for w in self.workers:
            w.join()
        self.workers.clear()


# 定义消费者函数
def kimi_work(factory: LLMFactory, work_func,
              work_id):
    """
    定义消费者函数
    factory： 工厂对象
    work_func：处理函数（输入job list和work_id）输出job_list和成功标志
    check_func: 检查是否可以拼接更多job,输出 布尔值
    """
    def __sleep(second: int):
        wake_up_time = time.time()+second
        while time.time() < wake_up_time:
            time.sleep(1)
            if factory.isFinish():
                break
    while not factory.isFinish():
        job = factory.get_job()
        if job is None:
            time.sleep(1)
            continue
        logger.debug(f"线程{work_id}，正在解析：{job}")
        res, kimi_status = work_func(job, work_id)
        # if kimi_status != TranslatorStatus.SUCCESS:
        #     logger.warning(f"线程{work_id}，获得结果失败，暂停5秒，重新处理JOBS")
        #     factory.reset_job(job, True)
        #     __sleep(5)
        if kimi_status == TranslatorStatus.FAILURE:
            logger.warning(f"线程{work_id}，获得结果失败,重新处理JOBS")
            factory.reset_job(job, True)
            # __sleep(120)
        elif kimi_status == TranslatorStatus.WAITING:
            logger.warning(f"线程{work_id}，要求超时等待，暂停1分30秒，重新处理JOBS")
            factory.reset_job(job, False)
            __sleep(90)
        else:
            factory.done_job(res)


if __name__ == "__main__":

    factory = LLMFactory(
        work_num=2,
        work_func=kimi_work,
        done_func=done_f,
        all_done_func=all_done_f
    )
    # # 启动线程
    # consumer_thread_1.start()
    # consumer_thread_2.start()
    factory.add_job("123")
    factory.add_job("234")
    factory.set_finish(True)
    factory.start_work()
# # 等待线程结束（这里为了演示，实际应用中应有适当的退出条件）
# consumer_thread_1.join()
# consumer_thread_2.join()
