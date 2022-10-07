###
 # @Author: lpdink
 # @Date: 2022-10-07 02:24:46
 # @LastEditors: lpdink
 # @LastEditTime: 2022-10-07 02:33:22
 # @Description: 通过source调用，添加当前脚本文件所在路径为PYTHONPATH，以方便测试文件从项目根目录引入模块
### 
ROOT_PATH=$(cd "$(dirname "$1")";pwd)
export PYTHONPATH="$ROOT_PATH:$PYTHONPATH"
