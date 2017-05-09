# If you're looking at this code, please know that I take no pride in it. It is
# some of the ugliest code I have ever written.
#
# If you want to make this web view actually usable, you probably want to scrap
# this and start again from square 0.

import sys
import os
import json
import cgi
import shutil

from collections import defaultdict

from util import DATE, NAME_BASE

BOOTSTRAP_CSS_URL = "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
BOOTSTRAP_CSS_LINK = '<link rel="stylesheet" href="{}">'.format(BOOTSTRAP_CSS_URL)

# If the native stacks contain any of these stack frames, we don't want to include them in our reports.
STACK_SKIP_LIST = [
    "BaseThreadInitThunk",
    "CharPrevA",
    "CsrAllocateMessagePointer",
    "DispatchMessageW",
    "DispatchMessageWorker",
    "EtwEventEnabled",
    "GetCurrentThread",
    "GetTickCount",
    "KiFastSystemCallRet",
    "MessageLoop::Run",
    "MessageLoop::RunHandler",
    "MsgWaitForMultipleObjects",
    "MsgWaitForMultipleObjectsEx",
    "NS_ProcessNextEvent",
    "NS_internal_main",
    "NtUserValidateHandleSecure",
    "NtWaitForAlertByThreadId",
    "NtWaitForMultipleObjects",
    "NtWaitForSingleObject",
    "PR_Lock",
    "PeekMessageW",
    "RealMsgWaitForMultipleObjectsEx",
    "RtlAnsiStringToUnicodeString",
    "RtlDeNormalizeProcessParams",
    "RtlEnterCriticalSection",
    "RtlLeaveCriticalSection",
    "RtlUserThreadStart",
    "RtlpAllocateListLookup",
    "RtlpDeCommitFreeBlock",
    "RtlpEnterCriticalSectionContended",
    "RtlpUnWaitCriticalSection",
    "RtlpWaitOnAddress",
    "RtlpWaitOnAddressWithTimeout",
    "RtlpWaitOnCriticalSection",
    "RtlpWakeByAddress",
    "UserCallWinProcCheckWow"
    "ValidateHwnd",
    "WaitForMultipleObjectsEx",
    "WaitForMultipleObjectsExImplementation",
    "WaitForSingleObjectEx",
    "XRE_InitChildProcess",
    "XRE_RunAppShell",
    "ZwWaitForMultipleObjects",
    "ZwWaitForSingleObject",
    "_RtlUserThreadStart",
    "__RtlUserThreadStart",
    "__scrt_common_main_seh",
    "content_process_main",
    "mozilla::BackgroundHangMonitor::NotifyActivity",
    "mozilla::BackgroundHangThread::NotifyActivity",
    "mozilla::BackgroundHangThread::NotifyWait",
    "mozilla::BootstrapImpl::XRE_InitChildProcess",
    "mozilla::HangMonitor::NotifyActivity",
    "mozilla::HangMonitor::Suspend",
    "mozilla::ValidatingDispatcher::Runnable::Run",
    "mozilla::detail::MutexImpl::lock",
    "mozilla::ipc::MessageChannel::MessageTask::Run",
    "mozilla::ipc::MessagePump::Run",
    "mozilla::ipc::MessagePumpForChildProcess::Run",
    "mozilla::widget::WinUtils::PeekMessageW",
    "mozilla::widget::WinUtils::WaitForMessage",
    "nsAppShell::ProcessNextNativeEvent",
    "nsAppShell::Run",
    "nsBaseAppShell::DoProcessNextNativeEvent",
    "nsBaseAppShell::OnProcessNextEvent",
    "nsBaseAppShell::Run",
    "nsThread::DoMainThreadSpecificProcessing",
    "nsThread::ProcessNextEvent",
    "wmain",
    "UserCallWinProcCheckWow",
    "ValidateHwnd",
    "0x1bc3d",
    "0x1905a",
    "RtlSleepConditionVariableCS",
    "SleepConditionVariableCS",
    "NDXGI::CDevice::GetKernelDeviceExecutionState",
    "NtGdiDdDDIGetDeviceState",
]

# Read in the symbolicated data into memory
with open('out/{}/hangs.json'.format(NAME_BASE)) as f:
    raw_hangs = json.load(f)

print "Data Read"

# Filter the very raw hangs into raw hangs
# raw_hangs = []
# for hang in very_raw_hangs:
#     for frame in hang['nativeStack']['symbolicatedStacks'][0]:
#         if frame in STACK_SKIP_LIST:
#             continue
#     raw_hangs.append(hang)

by_stack = defaultdict(list)
for hang in raw_hangs:
    by_stack[json.dumps(hang['stack'])].append(hang)

count_by_stack = defaultdict(int)
for key, hangs in by_stack.iteritems():
    for hang in hangs:
        count_by_stack[key] += 1

count_by_nativestack = defaultdict(int)
for hang in raw_hangs:
    count_by_nativestack[json.dumps(hang['nativeStack']['symbolicatedStacks'][0])] += 1

sorted_count_by_nativestack = sorted(count_by_nativestack.iteritems(), key=lambda (k, v): -v)

sorted_stacks = sorted(count_by_stack.keys(), key=lambda k: -count_by_stack[k])

print "Writing index.html"
# Create the index file
with open('out/{}/index.html'.format(NAME_BASE), 'w') as f:
    f.write("<!doctype html>\n")
    f.write(BOOTSTRAP_CSS_LINK + "\n")

    f.write('<div class="container">\n')
    f.write('<h1>{}</h1>\n'.format(DATE))
    f.write('<a href="all.html">all</a> <a href="hangs.json">json</a>')

    f.write('<table class="table">\n')
    f.write("<tr><th>Count</th><th>Stack</th><th>Link</th></tr>\n")
    for idx, stack in enumerate(sorted_stacks):
        f.write("<tr>\n")

        # Count
        f.write("<td>{}</td>\n".format(count_by_stack[stack]))

        # (pseudo-)Stack
        f.write("<td>\n")
        for seg in json.loads(stack):
            f.write(cgi.escape(seg) + "<br>\n")
        f.write("</td>\n")

        # Link to native stacks
        f.write('<td><a href="{}.html">link</a></td>'.format(idx))

        f.write("</tr>\n")
    f.write("</table>\n")
    f.write("</div>\n")


# Create each of the individual files
for idx, stack in enumerate(sorted_stacks):
    count_by_native_stack = defaultdict(int)
    for hang in by_stack[stack]:
        native = hang['nativeStack']['symbolicatedStacks'][0]
        count_by_native_stack[json.dumps(native)] += 1

    sorted_native_stacks = sorted(count_by_native_stack.iteritems(), key=lambda (ns, cnt): -cnt)

    print "Writing stacks for", idx

    with open('out/{}/{}.html'.format(NAME_BASE, idx), 'w') as f:
        f.write("<!doctype html>\n")
        f.write(BOOTSTRAP_CSS_LINK + "\n")

        f.write('<div class="container">\n')
        f.write('<h1>{}</h1>\n'.format(DATE))

        # Pseudostack
        f.write('<div>\n')
        for seg in json.loads(stack):
            f.write(cgi.escape(seg) + "<br>\n")
        f.write('</div>\n')

        # Histogram table
        f.write('<table class="table table-condensed">\n')
        f.write('<tr><th>Bucket</th><th>Count</th></tr>\n')
        final_hist = defaultdict(int)
        for hang in by_stack[stack]:
            for k, v in hang['histogram']['values'].iteritems():
                final_hist[k] += v

        for k, v in sorted(final_hist.iteritems(), key=lambda (k, v): int(k)):
            f.write('<tr><td>{}</td><td>{}</td></tr>'.format(k, v))

        f.write('</table>')

        # Native Stacks Table
        f.write('<table class="table">')
        f.write('<tr><th>#</th><th>Count</th><th>Native Stack</th></tr>')
        for idx, (ns, cnt) in enumerate(sorted_native_stacks):
            f.write('<tr>\n')
            f.write('<td><a href="#{0}" id="{0}">#</a></td>\n'.format(idx))
            f.write('<td>{}</td>\n'.format(cnt))
            f.write('<td>\n')
            for frame in json.loads(ns):
                f.write(cgi.escape(frame) + "<br>\n")
            f.write('</td>\n')
            f.write('</tr>\n')

        f.write('</table>\n')

        f.write('</div>\n')

print "Writing all data"

with open('out/{}/all.html'.format(NAME_BASE), 'w') as f:
    f.write("<!doctype html>\n")
    f.write(BOOTSTRAP_CSS_LINK + "\n")

    f.write('<div class="container">\n')
    f.write('<h1>ALL - {}</h1>\n'.format(DATE))

    f.write('<table class="table">')
    f.write('<tr><th>#</th><th>Count</th><th>Native Stack</th></tr>')
    for idx, (ns, cnt) in enumerate(sorted_count_by_nativestack):
        f.write('<tr>\n')
        f.write('<td><a href="#{0}" id="{0}">#</a></td>\n'.format(idx))
        f.write('<td>{}</td>\n'.format(cnt))
        f.write('<td>\n')
        for frame in json.loads(ns):
            f.write(cgi.escape(frame) + "<br>\n")
        f.write('</td>\n')
        f.write('</tr>\n')

    f.write('</table>\n')
    f.write('</div>\n')


