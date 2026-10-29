# 上传 GitHub 与发布文案

## 最短上传步骤

1. 打开 [预填信息的新建仓库页面](https://github.com/new?name=simulink-carsim-cosim-skill&owner=PengyuLaider&visibility=public&description=AI+workflow+for+building+and+verifying+Simulink+CarSim+co-simulation+projects)，确认 Owner 为 `PengyuLaider`，名称为 `simulink-carsim-cosim-skill`，选择 **Public**。可先勾选 Add README 方便进入文件列表；本包已有 MIT 许可证，无需另选。
2. 解压交付 ZIP，进入里面的 `simulink-carsim-cosim-skill`。在仓库选 **Add file → Upload files**，把该文件夹**里面的文件和子文件夹**一起拖入，保留 `skills/simulink-carsim-cosim/` 层级。不要只上传 ZIP，也不要再套一层同名文件夹。
3. 提交说明填 `Add Simulink CarSim co-simulation skill`。提交后检查 README、Skill 正文与 `docs/index.html` 均存在，图片能显示。

已有其他内容时，用新分支或 Pull Request 保留原文件。不要替换整个仓库。本地隐藏文件可能未被选中；`.gitignore` 只是辅助，核心 Skill 在 `skills/` 中。

官方参考：[添加文件](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)、[创建仓库](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)。

## 可复制的仓库资料

**名称**

```text
simulink-carsim-cosim-skill
```

**About 描述**

```text
An AI workflow skill for building inspectable Simulink models, integrating CarSim, debugging real solver feedback, and delivering reproducible co-simulation projects.
```

**建议 Topics**

```text
agent-skills  simulink  carsim  matlab  co-simulation  vehicle-dynamics  ai-assisted-development  verification
```

**中文分享文案**

```text
把一次智能泊车项目的 AI 协作经验，提炼成通用的 Simulink × CarSim Skill。

重点是建立可查看、可重建的 SLX，核对真实求解器接口，
用实际车辆反馈调试，并在同一版本完成回归与迁移验证。

包含工作流说明、故障分类、模型清点与源码指纹工具、离线展示页。
不绑定车型、算法或通道数，不包含 CarSim 求解器与车辆数据库。
```

`docs/index.html` 可离线打开。公开静态网站需另设 GitHub Pages；上传 HTML 本身不会生成公开网站。
