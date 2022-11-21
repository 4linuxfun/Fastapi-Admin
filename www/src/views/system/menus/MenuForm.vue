<template>
  <el-form-item label="菜单名称" prop="name" :rules="[{required:true,message:'请填写菜单名称'}]">
    <el-input v-model="selectData.name"></el-input>
  </el-form-item>
  <el-form-item v-if="selectData.type ==='subPage'" label="父菜单">
    <el-cascader v-model="selectData.parent_id" :options="cascaderMenu"
                 :props="{checkStrictly:true,value:'id',label:'name',emitPath:false}"
                 placeholder="请选择父菜单" style="width:100%">
    </el-cascader>
  </el-form-item>
  <el-form-item label="菜单路径" prop="path" :rules="[{required:true,message:'请填写菜单路径'}]">
    <el-input v-model="selectData.path"></el-input>
  </el-form-item>
  <el-form-item label="前端组件" prop="component"
                :rules="[{required:true,message:'一级菜单填写Layout'}]">
    <!-- <el-input v-if="selectData.parent_id == null" v-model="selectData.component" disabled></el-input> -->
    <el-input v-model="selectData.component"></el-input>
  </el-form-item>
  <el-form-item label="菜单图标" prop="icon">
    <el-input v-model="selectData.icon">
      <template #prepend>
        <el-icon>
          <component :is="selectData.icon"/>
        </el-icon>
      </template>
      <template #append>
        <el-button @click="dialogVisible=true">
          <el-icon>
            <Search/>
          </el-icon>
        </el-button>
      </template>
    </el-input>
  </el-form-item>
  <el-form-item label="排序" prop="sort">
    <el-input-number v-model="selectData.sort" :step="0.1"/>
  </el-form-item>
  <el-form-item label="状态">
    <auto-dict v-model="selectData.enable" type="switch" code="enable_code"/>
  </el-form-item>

  <!--  icon选择对话框-->
  <el-dialog v-model="dialogVisible">
    <el-tabs v-model="activeTab">
      <el-tab-pane v-for="(iconArray,name) in elementIcons" :label="name" :name="name" :key="name">
        <template v-for="(icon,index) in iconArray" :key="index">
          <el-button size="large" class="icon-style" @click="selectIcon=icon">
            <el-icon>
              <component :is="icon"/>
            </el-icon>
            <span>{{ icon }}</span>
          </el-button>
        </template>
      </el-tab-pane>
    </el-tabs>
    <template #footer>
      <el-button type="danger" @click="dialogVisible=false">取消</el-button>
      <el-button type="primary" @click="selectData.icon=selectIcon;dialogVisible=false">确认</el-button>
    </template>


  </el-dialog>
</template>

<script setup>
  import {toRefs, reactive, ref, watch, inject, computed} from 'vue'
  import useMenu from '@/composables/useMenu'
  import AutoDict from '@/components/AutoDict'

  const props = defineProps(['form', ])
  const emit = defineEmits(['update:form'])
  const {form} = toRefs(props)
  const dialogVisible = ref(false)
  const loading = ref(false)
  const menuData = inject('menuData')
  const {selectData, cascaderMenu} = useMenu(form.value, menuData.value, emit)
  const selectIcon = ref(null)
  const activeTab = ref('System')

  const elementIcons = {
    System: ['Plus', 'Minus', 'CirclePlus', 'Search', 'Female', 'Male', 'Aim',
      'House', 'FullScreen', 'Loading', 'Link', 'Service', 'Pointer', 'Star',
      'Notification', 'Connection', 'ChatDotRound', 'Setting', 'Clock', 'Position', 'Discount',
      'Odometer', 'ChatSquare', 'ChatRound', 'ChatLineRound', 'ChatLineSquare', 'ChatDotSquare', 'View',
      'Hide', 'Unlock', 'Lock', 'RefreshRight', 'RefreshLeft', 'Refresh', 'Bell',
      'MuteNotification', 'User', 'Check', 'CircleCheck', 'Warning', 'CircleClose', 'Close',
      'PieChart', 'More', 'Compass', 'Filter', 'Switch', 'Select', 'SemiSelect',
      'CloseBold', 'EditPen', 'Edit', 'Message', 'MessageBox', 'TurnOff', 'Finished',
      'Delete', 'Crop', 'SwitchButton', 'Operation', 'Open', 'Remove', 'ZoomOut',
      'ZoomIn', 'InfoFilled', 'CircleCheckFilled', 'SuccessFilled', 'WarningFilled', 'CircleCloseFilled', 'QuestionFilled',
      'WarnTriangleFilled', 'UserFilled', 'MoreFilled', 'Tools', 'HomeFilled', 'Menu', 'UploadFilled',
      'Avatar', 'HelpFilled', 'Share', 'StarFilled', 'Comment', 'Histogram', 'Grid',
      'Promotion', 'DeleteFilled', 'RemoveFilled', 'CirclePlusFilled'],
    Arrow: ['ArrowLeft', 'ArrowUp', 'ArrowRight', 'ArrowDown', 'ArrowLeftBold', 'ArrowUpBold', 'ArrowRightBold',
      'ArrowDownBold', 'DArrowRight', 'DArrowLeft', 'Download', 'Upload', 'Top', 'Bottom',
      'Back', 'Right', 'TopRight', 'TopLeft', 'BottomRight', 'BottomLeft', 'Sort',
      'SortUp', 'SortDown', 'Rank', 'CaretLeft', 'CaretTop', 'CaretRight', 'CaretBottom',
      'DCaret', 'Expand', 'Fold'],
    Document: ['DocumentAdd', 'Document', 'Notebook', 'Tickets', 'Memo', 'Collection', 'Postcard',
      'ScaleToOriginal', 'SetUp', 'DocumentDelete', 'DocumentChecked', 'DataBoard', 'DataAnalysis', 'CopyDocument',
      'FolderChecked', 'Files', 'Folder', 'FolderDelete', 'FolderRemove', 'FolderOpened', 'DocumentCopy',
      'DocumentRemove', 'FolderAdd', 'FirstAidKit', 'Reading', 'DataLine', 'Management', 'Checked',
      'Ticket', 'Failed', 'TrendCharts', 'List'],
    Media: ['Microphone', 'Mute', 'Mic', 'VideoPause', 'VideoCamera', 'VideoPlay', 'Headset',
      'Monitor', 'Film', 'Camera', 'Picture', 'PictureRounded', 'Iphone', 'Cellphone',
      'VideoCameraFilled', 'PictureFilled', 'Platform', 'CameraFilled', 'BellFilled'],
    Traffic: ['Location', 'LocationInformation', 'DeleteLocation', 'Coordinate', 'Bicycle', 'OfficeBuilding', 'School',
      'Guide', 'AddLocation', 'MapLocation', 'Place', 'LocationFilled', 'Van']
  }
  

</script>

<style scoped>
.icon-style {
  width: 200px;
  margin-left: 10px;
  margin-top: 10px;
}
</style>