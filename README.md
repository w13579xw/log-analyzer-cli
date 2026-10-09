# LogAnalyzer

LogAnalyzer 是一个用于解析和过滤服务器日志的 Python 命令行工具。它按行读取日志，支持筛选 `INFO`、`WARN`、`ERROR` 级别，并在控制台输出表格和统计摘要，也可以将匹配结果导出为 JSON 或 CSV。

## 环境依赖

- Python 3.9 或更高版本
- 运行时依赖：无第三方依赖，仅使用 Python 标准库
- 测试依赖：`pytest`（可选）

## 安装

在项目根目录执行：

```bash
python -m pip install .
```

安装测试依赖：

```bash
python -m pip install ".[test]"
```

## 启动

```bash
loganalyzer /path/to/server.log
```

只显示指定级别：

```bash
loganalyzer /path/to/server.log --level ERROR
loganalyzer /path/to/server.log --level WARN --level ERROR
```

导出匹配结果：

```bash
loganalyzer /path/to/server.log --output-format csv --output errors.csv --level ERROR
loganalyzer /path/to/server.log --output-format json --output errors.json --level ERROR
```

`--output-format` 支持 `csv` 和 `json`，并且必须与 `--output FILE` 一起使用。导出时，表格和统计摘要仍会输出到控制台。运行以下命令可查看全部参数：

```bash
loganalyzer --help
```

未安装时也可以从项目根目录直接运行：

```bash
python -m loganalyzer.cli /path/to/server.log --level ERROR
```

## 日志格式

解析器识别包含 `INFO`、`WARN` 或 `ERROR` 独立单词的日志行，级别匹配不区分大小写。级别之前的文本作为时间戳，之后的文本作为消息。例如：

```text
2026-10-08 10:15:30 INFO Server started
2026-10-08 10:16:02 [ERROR] Database unavailable
```

不包含支持级别的行会被忽略。输入必须是存在、非空的普通文件。日志按行流式处理，不会将整个文件载入内存。

## 测试

```bash
python -m pytest
```
