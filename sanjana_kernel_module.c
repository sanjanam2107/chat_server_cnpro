#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/sched.h>
#include <linux/string.h>
#include <linux/slab.h>
#include <linux/list.h>
#include <linux/sched/signal.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("SanjanaM");
MODULE_DESCRIPTION("OS_Project");
MODULE_ALIAS("sanjana_kernel_module");

struct pid_entry { 
    pid_t pid;
    struct list_head list;
};

static bool pid_seen(pid_t pid, struct list_head *seen_pids) {
    struct pid_entry *entry;
    list_for_each_entry(entry, seen_pids, list) {
        if (entry->pid == pid)
        return true;
    }
    return false;
}

static void pid_add(pid_t pid, struct list_head *seen_pids) {
    struct pid_entry *new_entry = kmalloc(sizeof(struct pid_entry), GFP_KERNEL);
    if (!new_entry)
    return;
    new_entry->pid = pid;
    list_add(&new_entry->list, seen_pids);
}

static void print_task(struct task_struct *task, int level, struct list_head *seen_pids) {
    struct task_struct *thread;
    struct list_head *thread_list;
    
    if (strcmp(task->comm, "thread_prg") != 0)
        return;
    
    if (!pid_seen(task->pid, seen_pids)) {
        printk(KERN_INFO "%*s Process: %s , Process ID : %d\n", level * 4, "", task->comm, task->pid);
        pid_add(task->pid, seen_pids);
    }
    
    list_for_each(thread_list, &task->thread_group) {
        thread = list_entry(thread_list, struct task_struct, thread_group);
        if (!pid_seen(thread->pid, seen_pids)) {
            printk(KERN_INFO "%*s Thread: %s , Thread ID : %d\n", (level + 1) * 4, "", thread->comm, thread->pid);
            pid_add(thread->pid, seen_pids);
        }
    }
    
    list_for_each(thread_list, &task->children) {
        thread = list_entry(thread_list, struct task_struct, sibling);
        print_task(thread, level + 1, seen_pids);
    }
}

static int __init start(void) {
    struct task_struct *task;
    struct list_head seen_pids;
    INIT_LIST_HEAD(&seen_pids);
    printk(KERN_INFO " MODULE LOADING INTO THE KERNEL.....\n");
 
    for_each_process(task)
        print_task(task, 0, &seen_pids);
    
    printk(KERN_INFO "MODULE LOADED SUCCESSFULLY\n");
    return 0;
}

static void __exit end(void) {
    printk(KERN_INFO "MODULE REMOVED FROM THE KERNEL\n");
}

module_init(start);
module_exit(end);
