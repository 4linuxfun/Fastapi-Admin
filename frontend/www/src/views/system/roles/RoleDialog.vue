<template>
  <el-dialog v-model="visible" title="角色编辑页面" width="50%" @close="visible = false" destroy-on-close>
    <el-form :model="selectData" label-width="80px" :rules="rules">
      <el-form-item label="角色名称" prop="name">
        <el-input v-model="selectData.name"></el-input>
      </el-form-item>
      <el-form-item label="角色描述">
        <el-input v-model="selectData.description"></el-input>
      </el-form-item>
      <el-form-item label="状态">
        <auto-dict v-model="selectData.enable" dict-type="switch" code="enable_code" />
      </el-form-item>
      <el-form-item label="菜单权限">
        <el-tree ref="menuTree" :data="menus" :props="defaultProps" accordion show-checkbox node-key="id"
          :default-checked-keys="enables" check-strictly @check="handleCheck">
          <template #default="{ data }">
            <div class="tree-node-content">
              <el-icon v-if="data.icon" class="node-icon" :class="getNodeIconClass(data)">
                <component :is="data.icon" />
              </el-icon>
              <span class="node-label" :class="getNodeLabelClass(data)">{{ data.name }}</span>
              <span class="node-tag" :class="getNodeTagClass(data)">{{ getNodeTypeText(data) }}</span>
            </div>
          </template>
        </el-tree>
      </el-form-item>
      <el-form-item>
        <el-button type="danger" @click="visible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate">确定</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import {
  GetRoleEnableMenus,
  PutRoles,
  PostNewRoles, GetRoleExist,
} from '@/api/roles'
import { ElNotification } from 'element-plus'
import AutoDict from '@/components/AutoDict'

const emit = defineEmits(['success'])
const visible = ref(false)
const selectData = reactive({})
const menus = ref([])
const defaultProps = reactive({
  children: 'children',
  label: 'name',
  class: customNodeClass
})
const enables = ref([])

//tree的用法
const menuTree = ref(null)

const rules = reactive({
  name: [{ required: true, trigger: 'blur', message: '请输入角色名' },
  {
    required: true, trigger: 'blur',
    validator: (rule, value, callback) => {
      GetRoleExist(selectData.name).then((response) => {
        if (response === 'error') {
          callback(new Error('角色名已存在'))
        } else {
          callback()
        }
      })
    }
  }]
})


function GetInfo() {
  console.log('id:' + selectData.id)
  GetRoleEnableMenus(selectData.id).then((response) => {
    console.log(response)
    menus.value = response.menus
    enables.value = response.enable
  })
}

function handleCheck(data, checked) {
  const tree = menuTree.value
  const isChecked = checked.checkedKeys.includes(data.id)
  
  if (isChecked) {
    // 选中子节点时，自动选中所有父节点
    checkParentNodes(data, tree)
  } else {
    // 取消选中父节点时，自动取消所有子节点
    uncheckChildNodes(data, tree)
  }
}

// 递归选中父节点
 function checkParentNodes(nodeData, tree) {
   const treeNode = tree.getNode(nodeData.id)
   if (treeNode && treeNode.parent && treeNode.parent.key) {
     const parentId = treeNode.parent.key
     const checkedKeys = tree.getCheckedKeys()
     if (!checkedKeys.includes(parentId)) {
       tree.setChecked(parentId, true, false)
       // 继续向上检查父节点
       const parentNodeData = treeNode.parent.data
       if (parentNodeData) {
         checkParentNodes(parentNodeData, tree)
       }
     }
   }
 }

// 递归取消选中子节点
function uncheckChildNodes(node, tree) {
  if (node.children && node.children.length > 0) {
    node.children.forEach(child => {
      tree.setChecked(child.id, false, false)
      uncheckChildNodes(child, tree)
    })
  }
}

async function handleUpdate() {
  let checkedKeys = menuTree.value.getCheckedKeys().concat(menuTree.value.getHalfCheckedKeys())
  console.log(checkedKeys)
  selectData.menus = checkedKeys
  console.log(selectData)
  if (selectData.id === null) {
    try {
      await PostNewRoles(selectData)
      ElNotification({
        title: 'success',
        message: '角色新建成功',
        type: 'success'
      })
    } catch (error) {
      ElNotification({
        title: 'error',
        message: '角色新建失败：' + error,
        type: 'error'
      })
    }
  } else {
    try {
      await PutRoles(selectData)
      ElNotification({
        title: 'success',
        message: '角色更新成功',
        type: 'success'
      })
    } catch (error) {
      ElNotification({
        title: 'error',
        message: '失败：' + error,
        type: 'error'
      })
    }
  }
  visible.value = false
  emit('success')
}

function customNodeClass(data, node) {
  if (data.type === 'btn') {
    return 'is-btn'
  }
  return null
}

function getNodeTypeText(data) {
  if (data.type === 'btn') {
    return '按钮'
  } else if (data.type === 'page' || data.type === 'subPage') {
    return '菜单'
  }
  return '菜单'
}

function getNodeIconClass(data) {
  if (data.type === 'btn') {
    return 'button-icon'
  }
  return 'menu-icon'
}

function getNodeLabelClass(data) {
  if (data.type === 'btn') {
    return 'button-label'
  }
  return ''
}

function getNodeTagClass(data) {
  if (data.type === 'btn') {
    return 'button-tag'
  }
  return 'menu-tag'
}

function add() {
  Object.assign(selectData, {
    id: null,
    name: '',
    description: '',
    enable: true
  })
  GetInfo()
  visible.value = true
}

function edit(role) {
  Object.assign(selectData, role)
  GetInfo()
  visible.value = true
}


defineExpose({ add, edit })

</script>

<style>
/* .el-tree-node.is-expanded.is-btn>.el-tree-node__children {
  display: flex;
  flex-direction: column;
} */

/* 标签样式 - tag效果 */
.node-tag {
  flex-shrink: 0;
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 3px;
  margin-left: 12px;
  font-weight: 500;
  line-height: 1.2;
  display: inline-block;
  white-space: nowrap;
}

/* 菜单类型标签 */
.node-tag.menu-tag {
  background-color: #e1f5fe;
  color: #0277bd;
  border: 1px solid #b3e5fc;
}

/* 按钮类型标签 */
.node-tag.button-tag {
  background-color: #fff3e0;
  color: #ef6c00;
  border: 1px solid #ffcc02;
}
</style>
