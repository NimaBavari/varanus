# Varanus

Simple monitoring daemon service.

## Overview

- Type-checked, documented codebase.
- Fully covered with exception handling: no invisible cases.
- In-house implemented concurrency (scheduler, worker, etc.): no external libraries.
- No use of any third party libraries in general; the system was built with only the Python standard library. There are some dev dependencies though for the codebase quality check CI workflow.
- File-based SQLite database with optimised connection acquisition.

Please, see the docstrings and comments for more granular descriptions.

See also: [Usage](#usage) and [Scripts](#scripts).

## Usage

Go to `config.py` and set your resources. Resources are a list of URLs; period and the regexp pattern (or the lack thereof) is configured on a per-URL basis. An example `resources` list is already configured but you can change it. 

Task execution follows an interface (`TaskHandler`); you can define your custom task execution function, obeying the signature. One such function is already implemented: see `handle_task` in `task.py`. The class `Task` takes a task handler function as an argument.

Run:

```console
make start
```

to spin up the system.

## Scripts

Run:

```console
make code-quality
```

to clean up the codebase if you ever touch it.
