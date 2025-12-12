# Indented Logger
An extension of the standard logging package, supplying:
- block indentation,
- severity coloring,
- default formatting and saving,
- dedicated level for control flow tracing.

## Contents
1. [Installation](#installation)
2. [Usage](#usage)
    + [Setup](#setup)
    + [Indentation](#indentation)
    + [Verbosity levels](#verbosity)
    + [Namespace](#namespace)
    + [Message prefix](#message)
    + [Automated logging](#automation)
    + [Tracing recommendation](#tracing)

<h2 id="installation">
1. Installation
</h2>


### 1.1 From PyPI index
The most straightforward way:
```shell
$ pip install indelog
```

### 1.2 From GitHub sources
If you plan to play with the code and make improvements, use editable mode with `dev` dependencies:
```shell
$ git clone https://github.com/petergee302/indelog.git .
$ pip install -e .[dev]
```
Run static code analysis and automated tests before each push:
```shell
$ pyright
$ pytest -vs
```


<h2 id="usage">
2. Usage
</h2>

<h3 id="setup">
2.1 Setup
</h3>

The recommended way to initialize and configure this logger is to use the `with ilog.Setup(...)` clause which guarantees the entry/exit points to be executed:
```python
import ilog
...
with ilog.Setup() as logger:
    ...
```
There are several options to this object that control _e.g._ the global level or output file:
- `global_level` (`str` or `int` from `ilog.LEVELS`):
    Verbosity level to set for the logger. Can be either the name or the numerical value corresponding to the level. The default value of `logging.NOTSET` does not change current threshold.
- `output_path` (`str` or `Path`):
    Where to save the log file: This can be either complete file path, or a directory. In the latter case `module_fname` is required.
- `module_fname`:
    If given, its base name will be combined with given directory path and extension to build module-related log file. For instance `train.py` will become
        `<output_path>/train.log`
- `namespace` (`str`):
    If given, overrides the namespace
- `colorize` (`bool`):
    Enable/disable colored console output (notice, if enabled the escape sequences also appear in the file)
- `line_format` (`str`):
    Message prefix to override the default format.

#### Example:
Create `<module>-<timestamp>.log` file besides the executing `<module>.py` file. All messages within the two trace calls will be indented at least once.
```python
import ilog
...
if __name__ == '__main__':
    with ilog.Setup(ilog.TRACE, __file__) as logger:
        logger.trace(f'> main')
        ...
        logger.trace(f'< main')
```

<h3 id="indentation">
2.2 Indentation
</h3>

The major shortcoming of the default logging module is the lack of block indentation mechanism. This is particularly painful when trying to analyze the control flow of a long, real-time, multi-turn, possibly multi-threaded or asynchronous code, like user interaction, or REST interface of a service. Debugging is basically excluded in these cases, and simple status printing does very poor job, if any.

Log indentation serves the same purpose as indentation of the code that generated it: To structure the flow into nested blocks that are much easier to understand. The difference is that while the code reflects the 'spatial' structure of an algorithm, the logs are its 'temporal' signature.

In Python one can use decorators to capture the entry and exit points of a function or method, nevertheless it is not recommended to use it as default means of logging due to (_i_) noticeable overhead, and (_ii_) lack of control over the selection and format of arguments and returned values.

<!--
There are mechanisms in Python that allow for capture of function entry and exit points (_e.g._ `functools.wraps`)
-->
In this module we use manual marking of the entry and exit points of a block. This has some pros and cons of course, but the need to control what and how to log is definitely more important than a desire to just dump everything automatically on a single press of a button.

There are two indentation markers:
- `>` = begin indented block starting next line
- `<` = end of a block and unindent

#### Example:
```python
def fun() -> int:
    logger.debug('> fun()')
    result = gun(2)//3
    logger.debug('< fun(): %d', result)
    return result

def gun(arg :int) -> int:
    logger.debug('> gun(arg=%d)', arg)
    result = 5*hun(arg + 1)
    logger.debug('< gun(): %d', result)
    return result

def hun(arg :int) -> int:
    result = 13 + arg
    logger.debug('hun(arg=%d): %d', arg, result)
    return result
```
The above code would give output like this:
```text
🔎 DEBUG   2025-11-26 14:13:23.731 78F45860B080 > fun()
🔎 DEBUG   2025-11-26 14:13:23.732 78F45860B080   > gun(arg=2)
🔎 DEBUG   2025-11-26 14:13:23.732 78F45860B080     hun(arg=3): 16
🔎 DEBUG   2025-11-26 14:13:23.732 78F45860B080   < gun(): 80
🔎 DEBUG   2025-11-26 14:13:23.732 78F45860B080 < fun(): 26
```
Notice that
(_i_) the indentation is used only in nested functions; there's no point in nesting inside `hun()` because it neither calls any other function that logs, nor performs any time-consuming work.
(_ii_) we use consistent convention to format the arguments and returned values. more on that in the last section.

<h3 id="verbosity">
2.3 Verbosity levels
</h3>

Verbosity level is a severity threshold above which messages are passed to the handlers. There is one global level set by either:
- `ILOG_VERBOSITY_LEVEL = ...` environment variable, or
- `Setup(global_level = ...)` argument during initialization

And there are local levels which can be set when fetching local loggers:
- `getLogger(local_level = ...)`

The effective level within module is the maximum of the two, for instance:
```text
    local  global  effective
    -----  ------  ---------
    DEBUG   INFO     INFO
    ERROR   INFO     ERROR
```
<h4 style="color:violet">
💀 FATAL:
</h4>

This level indicates a critical error that causes the application to abort or terminate. It is used for unrecoverable errors that require immediate attention, such as a system crash or an application shutdown.

<h4 style="color:red">
💥 ERROR:
</h4>

This level signifies a significant problem that prevents a specific operation from being completed. While the application may continue running, this level alerts teams to critical issues that need immediate investigation and resolution.

<h4 style="color:yellow">
⚠️ WARNING:
</h4>

This level is used for unexpected events that do not prevent the application from functioning but may indicate potential problems. It is often used to signal conditions that are close to causing errors, such as approaching resource limits.

<h4 style="color:white">
💬 INFO:
</h4>

This level is used for general operational messages that provide information about the normal flow of the application. It is suitable for tracking typical operations, such as successful logins or service startups.

<h4 style="color:green">
🐾 TRACE:
</h4>

This level is used for tracing the execution flow of the application, and is not part of the standard Python logger. It is typically employed during development or debugging sessions to monitor the sequence of function calls and execution paths. Trace logs should provide object types and unique identifiers of their instances to allow object-level resolution of information.

<h4 style="color:cyan">
🔎 DEBUG:
</h4>

This level provides the most detailed information useful for diagnosing problems. It is typically used during development or troubleshooting to trace application state, variable values, and business logic decisions. Since this type of logs may output frequently and in large volumes necessary to understand particular problem, it may have significant impact on the performance. Python does not have preprocessor like C/C++ which could automatically eliminate preparation of data for such calls, the only available remedies are to condition the `logger.debug()` call, or simply not to push such debug logs to the repository.

<h3 id="namespace">
2.4 Namespace
</h3>

The `IndentedLogger` derives from, but does not modify the default root logger. Hence, all its instances must have non-empty _namespace_ i.e. a name prefix distinguishing from loggers created by other packages in use. There are two ways the namespace may be specified by:
- `ILOG_NAMESPACE = ...` environment variable, or by
- `Setup(namespace = ...)` argument during initialization


<h3 id="message">
2.5 Message prefix
</h3>

By default all output messages are prefixed with additional information containing the event severity, its ISO date-time up to millisecond, and the thread ID of origin. Examples are given below:
```text
💥 ERROR   2019-02-27 02:13:24.632 753DCED0A180 TrainingHistory.teardown(): UNEXPECTED_CALL
⚠️ WARNING 2020-12-01 12:58:34.763 7F46F17AA700 Job d50395084c9f4cfdb0c73190b740465d already removed
🐾 TRACE   2023-06-08 21:04:45.158 7036CCD1D080 DensityMatrix[7035BB4622D0](size=2)
🔎 DEBUG   2025-10-21 11:26:05.830 78F45860B080 n_samples=5674
```
The second part of the prefix can be modified (e.g. the thread ID removed, if not needed) by either:
- `ILOG_LINE_FORMAT` environment variable, or by
- `Setup(line_format = ...)` argument during initialization


<h3 id="automation">
2.6 Automated logging
</h3>

As projects get shorter and shorter time-frames, hardly anyone has enough patience to go through the entire code weaving in such a lines. For those who seek error-resistance and uniformity despite lesser control and bigger overhead, there are set of decorators that make the logging automated.
There are two kind of each:
<table>
    <tr>
        <td>
            call
        </td>
        <td>
            Log arguments and result after exit of a function/method
        </td>
    </tr>
    <tr>
        <td>
            block
        </td>
        <td>
            Log arguments before the entry of a function/method, and result after its exit
        </td>
    </tr>
</table>

They operate on function, method, and whole class level (the latter may be particularly useful if you just need to trace your code execution, but have no time for applying the logs):
<table>
    <tr>
        <td>function-level</td>
        <td style="font-family:courier;text-align:right">
             @fatal_function_call(), <br>
             @error_function_call(), <br>
           @warning_function_call(), <br>
              @info_function_call(), <br>
             @trace_function_call(), <br>
             @debug_function_call(), <br>
             @fatal_function_block(),<br>
             @error_function_block(),<br>
           @warning_function_block(),<br>
              @info_function_block(),<br>
             @trace_function_block(),<br>
             @debug_function_block(),
        </td>
    </tr>
    <tr>
        <td>method-level</td>
        <td style="font-family:courier;text-align:right">
              @fatal_method_call(), <br>
              @error_method_call(), <br>
            @warning_method_call(), <br>
               @info_method_call(), <br>
              @trace_method_call(), <br>
              @debug_method_call(), <br>
              @fatal_method_block(),<br>
              @error_method_block(),<br>
            @warning_method_block(),<br>
               @info_method_block(),<br>
              @trace_method_block(),<br>
              @debug_method_block(),
        </td>
    </tr>
    <tr>
        <td>class-level</td>
        <td style="font-family:courier;text-align:right">
              @fatal_calls(), <br>
              @error_calls(), <br>
            @warning_calls(), <br>
               @info_calls(), <br>
              @trace_calls(), <br>
              @debug_calls(), <br>
              @fatal_blocks(),<br>
              @error_blocks(),<br>
            @warning_blocks(),<br>
               @info_blocks(),<br>
              @trace_blocks(),<br>
              @debug_blocks(),
        </td>
    </tr>
</table>

The drawbacks of using automated logs is that
-  there's no control over which arguments and return values are serialized, what sometimes may backfire resulting in a cluttered and _less_ readable console output, instead of a clear trace.
- they do not capture any internal working of a function/method, nor signal any state or stage changes; they are primarily intended for tracing.

#### Example:
Instead of
```python
def fun() -> int:
    logger.debug('> fun()')
    result = ...
    logger.debug('< fun(): %d', result)
    return result
```
One can equivalently write
```python
@debug_function_block(logger)
def fun() -> int:
    result = ...
    return result
```
Instead of painstakingly applying logs to all methods of a class
```python
class A:
    def __init(self, ...):
        logger.trace(...)
        ...
```
you can simply use class-level decorator
```python
@trace_calls(logger)
class A:
    def __init(self, ...):
        ...
```

<h3 id="tracing">
2.7 Tracing recommendation
</h3>

Standard Python logger is not designed with execution tracing in mind, thus there's no `TRACE` level, nor there's a convention on what and when to log. Herein we outline such proposal based on past experiences from over a couple of decades.

1. First of all, log the creation of objects (in C/C++ we'd also log destruction thereof).
2. Unless the object is a singleton, log its unique ID for the sake of distinguishing them in the trace, for example:
    ```python
    def __init__(self, arg1 :int, arg2 :bool):
        logger.trace(f'ClassName[{id(self):012X}]({arg1=}, {arg2=})')
    ```

3. Unless the class is final replace the explicit `ClassName` above with `{type(self).__name__}` in order to make dynamic substitution:
    ```python
    def __init__(self, arg1 :int, arg2 :bool):
        logger.trace(f'{type(self).__name__}[{id(self):012X}]({arg1=}, {arg2=})')
    ```

4. If the function or method is time-consuming, may crash, or causes other log messages to appear, use indentation with at least two messages marking both entry and exit points:
    ```python
    def method(self, arg3 :str) -> float:
        logger.trace(f'> {type(self).__name__}[{id(self):012X}].method({arg3=})')
        ...
        logger.trace(f'< {type(self).__name__}[{id(self):012X}].method(): {result=}')
        return result
    ```
    Do not use indentation in functions or methods that are quick to complete and do not invoke other logging code.

5. The above logs are pretty standard, but long enough to make room for mistakes. In order to reduce their chances, bring the number of return statements to bare minimum, ideally to just one. That means instead of the usual code like:
    ```python
    if condition-one:
        logger.trace(f'< some_function(): {x}')
        return x
    ...
    if condition-two:
        logger.trace(f'< some_function(): {y}')
        return y
    ...
    logger.trace(f'< some_function(): {z}')
    return z
    ```
    write
    ```python
    if condition-one:
        result = x
    else:
        ...
        if condition-two:
            result = y
        else:
            ...
            result = z
    logger.trace(f'< some_function(): {result}')
    return result
    ```
    or use function/method/class decorators to automate logging.

6. In order to reduce chances for mistakes and inconsistency, prefer automated logging over manual. It is also the easier way to start with.

    Use manual logging if the automated one is insufficient, _e.g._: it formats and prints large values which are not particularly important, or prints too much or too little, inundates the stream or does not capture some important elements.


-----------------------------------
Copyright © 2018-2025 Peter Gee<br>
MIT License
