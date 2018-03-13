# QJZeditor

This is a project for the BBS site in Peking University, BDWM BBS. For the sake of the target users, all documentations as well as code comments and outputs are in Chinese.

Please contact the developer for futher information. Thank you!

## 已知错误

* **解压缩的目标文件路径中不能有中文。建议仅使用大小写罗马字母和下划线命名文件夹，且不要用空格。**
* **配合2018年的`QJZansisource.ans`，在三行模式显示采编名单时，第三行会出现一个额外的空格。**

## 说明

本程序是北大未名BBS起居注编辑部对未名起居注进行自动化排版的工具。本工具目前是2.3.1版，需使用Python 2.7运行。目前只稳定支持Windows。

原先GitHub对于中文编码和Windows换行模式不甚支持，以至于无法使用这一平台。近来GitHub改进了这方面的支持，因此将历史代码迁移与此。

由于种种原因，本项目原则上已经停止开发。

## 对主编

请先阅读`Readme.txt`中的内容。

请按照`QJZeditor_2_2.pdf`中的使用方法进行操作。注意[该文档](https://github.com/MengXiangxi/QJZeditor/wiki/QJZEditor-2.2-%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E)已经过时了，但是作者一直没有更新。实际上这个文档仍然很有参考价值。

[点此下载zip压缩包。](https://github.com/MengXiangxi/QJZeditor/archive/master.zip)

## 注意事项

以下注意事项来自北大未名BBS内部版面。因为迁移程序的原因转录于此。

>为了减少主编的工作量，请采编尽量直接按照程序可处理的格式发文。主要需要注意的问题如下：
>
>* 每天 0-9 区必须每个区都发帖子，即便没有内容。
>* 如果该区没有采内容，则在标题后面加“kong”或“void”。以下四种情况是可以接受的：“0@0209kong”，“0@0209 kong”，“0@0209void”，“0@0209 void”。
>* 今日热点（如果有）的标题，必须以“H”或“h”开头。
>* 内容从第一行开始写，之前不要有空行。
>* 版名独占一行，版名和内容之间没有空行。多个版面之间只空一行。空行不得有任何字符，包括空格。
>* 如果某一行要用灰字，请在行首加一个下划线“_”。
>* 每个分区的主题贴中，请不要有其他内容。如果有任何评论，最好跟贴。

## 更新记录

QJZEditor正式版：

### QJZEditor 2.2 2016-Mar-06

 1. 各种bug修复。
 2. 行末标点符号检查。
 3. “Powered by”行。

### QJZEditor 2.2 release 2016-Mar-06

1. 修改了模板。
2. 增加了供Windows运行的Windows可执行文件（临时性措施）。感谢 @cyblocker 帮助封装成EXE！

### QJZEditor 2.3.1 2017-Feb-07

1. 修改了左下角年份的ASCIIArt。
2. 归档了一些过时的文件和程序。
3. 修改了主程序以适应新的ASCIIArt年份图标。

Note:请务必更新到最新版本！新版中，主程序和QJZansisource.ans都有变更。Editors.ans可以不必更新。

### 2017-Mar-04 停止更新和支持

上传了最新版的editors.ans。
