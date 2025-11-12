<template>
  <div class="map-picker">
    <!-- 引擎切换器 -->
    <div class="engine-switcher">
      <el-segmented v-model="mapEngine" :options="engineOptions" size="small">
        <template #default="{ item }">
          <div class="engine-option">
            <span>{{ item.label }}</span>
          </div>
        </template>
      </el-segmented>
    </div>

    <!-- 地点搜索框 -->
    <div class="search-box">
      <el-input
        v-model="searchKeyword"
        :placeholder="`搜索地点（当前：${mapEngine === 'baidu' ? '百度地图' : '高德地图'}）`"
        clearable
        @keyup.enter="searchLocation"
      >
        <template #prefix>
          <i class="bi bi-search"></i>
        </template>
        <template #append>
          <el-button @click="searchLocation" :loading="searching">
            搜索
          </el-button>
        </template>
      </el-input>
    </div>

    <!-- 搜索结果列表 -->
    <div v-if="searchResults.length > 0" class="search-results">
      <div
        v-for="(result, index) in searchResults"
        :key="index"
        class="result-item"
        @click="selectLocation(result)"
      >
        <i class="bi bi-geo-alt-fill"></i>
        <div class="result-info">
          <div class="result-name">{{ result.title }}</div>
          <div class="result-address">{{ result.address }}</div>
        </div>
      </div>
    </div>

    <!-- 地图容器 -->
    <div :id="mapContainerId" class="map-container"></div>

    <!-- 当前选中的位置 -->
    <div v-if="selectedLocation" class="selected-location">
      <div class="location-info">
        <i class="bi bi-geo-alt text-primary"></i>
        <div>
          <div class="location-name">{{ selectedLocation.name }}</div>
          <div class="location-address">{{ selectedLocation.address }}</div>
          <div class="location-coords">
            经度: {{ selectedLocation.lng.toFixed(6) }}, 
            纬度: {{ selectedLocation.lat.toFixed(6) }}
          </div>
        </div>
      </div>
      <el-button type="danger" size="small" @click="clearLocation">
        <i class="bi bi-x-circle"></i> 清除
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  initialLocation: {
    type: Object,
    default: null
  },
  initialLat: {
    type: Number,
    default: null
  },
  initialLng: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:location'])

// 引擎选择
const mapEngine = ref('baidu')
const engineOptions = [
  { label: '百度地图', value: 'baidu' },
  { label: '高德地图', value: 'amap' }
]

// 地图实例（通用）
let mapInstance = null
let markerInstance = null
let geocoderInstance = null

// 搜索相关
const searchKeyword = ref('')
const searchResults = ref([])
const searching = ref(false)
const selectedLocation = ref(null)

// 地图容器ID（动态生成，避免冲突）
const mapContainerId = ref('map-container-' + Math.random().toString(36).substr(2, 9))

// 百度地图初始化
const initBaiduMap = () => {
  if (typeof BMap === 'undefined') {
    ElMessage.error('百度地图SDK加载失败')
    return false
  }

  try {
    mapInstance = new BMap.Map(mapContainerId.value)
    geocoderInstance = new BMap.Geocoder()

    const initPoint = props.initialLat && props.initialLng
      ? new BMap.Point(props.initialLng, props.initialLat)
      : new BMap.Point(116.404, 39.915) // 北京天安门

    mapInstance.centerAndZoom(initPoint, 15)
    mapInstance.enableScrollWheelZoom(true)

    // 添加控件
    mapInstance.addControl(new BMap.NavigationControl({
      anchor: BMAP_ANCHOR_TOP_LEFT,
      type: BMAP_NAVIGATION_CONTROL_SMALL
    }))
    mapInstance.addControl(new BMap.ScaleControl())

    // 点击事件
    mapInstance.addEventListener('click', (e) => {
      const point = e.point
      addBaiduMarker(point)
      
      geocoderInstance.getLocation(point, (result) => {
        if (result) {
          selectedLocation.value = {
            name: result.address,
            address: result.addressComponents.province + 
                     result.addressComponents.city + 
                     result.addressComponents.district + 
                     result.addressComponents.street + 
                     result.addressComponents.streetNumber,
            lng: point.lng,
            lat: point.lat
          }
          emit('update:location', selectedLocation.value)
        }
      })
    })

    // 如果有初始位置，添加标记
    if (selectedLocation.value) {
      addBaiduMarker(initPoint, selectedLocation.value.name)
    }

    return true
  } catch (error) {
    console.error('百度地图初始化失败:', error)
    ElMessage.error('百度地图初始化失败')
    return false
  }
}

// 高德地图初始化
const initAmapMap = () => {
  if (typeof AMap === 'undefined') {
    ElMessage.error('高德地图SDK加载失败')
    return false
  }

  try {
    const center = props.initialLat && props.initialLng
      ? [props.initialLng, props.initialLat]
      : [116.404, 39.915] // 北京天安门

    mapInstance = new AMap.Map(mapContainerId.value, {
      zoom: 15,
      center: center,
      resizeEnable: true
    })

    geocoderInstance = new AMap.Geocoder()

    // 点击事件
    mapInstance.on('click', (e) => {
      const lnglat = e.lnglat
      addAmapMarker(lnglat)

      geocoderInstance.getAddress([lnglat.lng, lnglat.lat], (status, result) => {
        if (status === 'complete' && result.info === 'OK') {
          const addressComponent = result.regeocode.addressComponent
          selectedLocation.value = {
            name: result.regeocode.formattedAddress,
            address: addressComponent.province + 
                     addressComponent.city + 
                     addressComponent.district + 
                     addressComponent.street + 
                     addressComponent.streetNumber,
            lng: lnglat.lng,
            lat: lnglat.lat
          }
          emit('update:location', selectedLocation.value)
        }
      })
    })

    // 如果有初始位置，添加标记
    if (selectedLocation.value) {
      addAmapMarker(center, selectedLocation.value.name)
    }

    return true
  } catch (error) {
    console.error('高德地图初始化失败:', error)
    ElMessage.error('高德地图初始化失败')
    return false
  }
}

// 百度地图添加标记
const addBaiduMarker = (point, label = '选中位置') => {
  if (markerInstance) {
    mapInstance.removeOverlay(markerInstance)
  }
  
  markerInstance = new BMap.Marker(point)
  mapInstance.addOverlay(markerInstance)
  
  const markerLabel = new BMap.Label(label, { offset: new BMap.Size(20, -10) })
  markerInstance.setLabel(markerLabel)
  
  mapInstance.panTo(point)
}

// 高德地图添加标记
const addAmapMarker = (lnglat, label = '选中位置') => {
  if (markerInstance) {
    mapInstance.remove(markerInstance)
  }
  
  markerInstance = new AMap.Marker({
    position: lnglat,
    title: label
  })
  
  mapInstance.add(markerInstance)
  mapInstance.setCenter(lnglat)
}

// 百度地图搜索
const searchBaiduLocation = () => {
  const local = new BMap.LocalSearch(mapInstance, {
    onSearchComplete: (results) => {
      searching.value = false
      
      if (local.getStatus() === BMAP_STATUS_SUCCESS) {
        const tempResults = []
        for (let i = 0; i < results.getCurrentNumPois(); i++) {
          const poi = results.getPoi(i)
          tempResults.push({
            title: poi.title,
            address: poi.address,
            point: poi.point,
            engine: 'baidu'
          })
        }
        searchResults.value = tempResults
        
        if (tempResults.length === 0) {
          ElMessage.info('未找到相关地点')
        } else {
          ElMessage.success(`找到 ${tempResults.length} 个地点`)
        }
      } else {
        ElMessage.error('搜索失败，请重试')
      }
    }
  })
  
  local.search(searchKeyword.value)
}

// 高德地图搜索
const searchAmapLocation = () => {
  AMap.plugin('AMap.PlaceSearch', () => {
    const placeSearch = new AMap.PlaceSearch({
      city: '全国'
    })
    
    placeSearch.search(searchKeyword.value, (status, result) => {
      searching.value = false
      
      if (status === 'complete' && result.info === 'OK') {
        const pois = result.poiList.pois
        const tempResults = pois.map(poi => ({
          title: poi.name,
          address: poi.address,
          point: poi.location,
          engine: 'amap'
        }))
        
        searchResults.value = tempResults
        
        if (tempResults.length === 0) {
          ElMessage.info('未找到相关地点')
        } else {
          ElMessage.success(`找到 ${tempResults.length} 个地点`)
        }
      } else {
        ElMessage.error('搜索失败，请重试')
      }
    })
  })
}

// 搜索地点（统一入口）
const searchLocation = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  searching.value = true
  searchResults.value = []

  try {
    if (mapEngine.value === 'baidu') {
      searchBaiduLocation()
    } else {
      searchAmapLocation()
    }
  } catch (error) {
    searching.value = false
    ElMessage.error('搜索出错：' + error.message)
  }
}

// 选择搜索结果
const selectLocation = (result) => {
  if (result.engine === 'baidu') {
    const point = result.point
    selectedLocation.value = {
      name: result.title,
      address: result.address,
      lng: point.lng,
      lat: point.lat
    }
    addBaiduMarker(point, result.title)
  } else {
    const lnglat = result.point
    selectedLocation.value = {
      name: result.title,
      address: result.address,
      lng: lnglat.lng,
      lat: lnglat.lat
    }
    addAmapMarker(lnglat, result.title)
  }
  
  searchResults.value = []
  searchKeyword.value = ''
  emit('update:location', selectedLocation.value)
  ElMessage.success('已选择：' + result.title)
}

// 清除选中的位置
const clearLocation = () => {
  selectedLocation.value = null
  
  if (mapEngine.value === 'baidu' && markerInstance) {
    mapInstance.removeOverlay(markerInstance)
  } else if (mapEngine.value === 'amap' && markerInstance) {
    mapInstance.remove(markerInstance)
  }
  
  markerInstance = null
  emit('update:location', null)
  ElMessage.info('已清除地点')
}

// 切换地图引擎
const switchMapEngine = async () => {
  // 清理旧地图
  if (mapInstance) {
    if (mapEngine.value === 'baidu') {
      mapInstance.destroy?.()
    } else {
      mapInstance.destroy()
    }
    mapInstance = null
    markerInstance = null
  }

  searchResults.value = []
  
  await nextTick()
  
  // 初始化新地图
  if (mapEngine.value === 'baidu') {
    initBaiduMap()
  } else {
    initAmapMap()
  }
  
  ElMessage.success(`已切换到${mapEngine.value === 'baidu' ? '百度地图' : '高德地图'}`)
}

// 监听引擎切换
watch(mapEngine, () => {
  switchMapEngine()
})

// 初始化
onMounted(() => {
  // 设置初始位置
  if (props.initialLocation && props.initialLat && props.initialLng) {
    selectedLocation.value = {
      name: props.initialLocation.name || '已选位置',
      address: props.initialLocation.address || '',
      lng: props.initialLng,
      lat: props.initialLat
    }
  }

  // 从localStorage恢复上次选择的引擎
  const savedEngine = localStorage.getItem('map_engine')
  if (savedEngine && (savedEngine === 'baidu' || savedEngine === 'amap')) {
    mapEngine.value = savedEngine
  }

  // 初始化地图
  if (mapEngine.value === 'baidu') {
    initBaiduMap()
  } else {
    initAmapMap()
  }
})

// 保存引擎选择
watch(mapEngine, (newEngine) => {
  localStorage.setItem('map_engine', newEngine)
})
</script>

<style scoped>
.map-picker {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.engine-switcher {
  display: flex;
  justify-content: center;
  padding: 8px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.engine-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
}

.search-box {
  width: 100%;
}

.search-results {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: white;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.result-item:last-child {
  border-bottom: none;
}

.result-item:hover {
  background-color: #f5f7fa;
}

.result-item i {
  font-size: 20px;
  color: #667eea;
}

.result-info {
  flex: 1;
}

.result-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.result-address {
  font-size: 13px;
  color: #909399;
}

.map-container {
  width: 100%;
  height: 400px;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
}

.selected-location {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.location-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex: 1;
}

.location-info i {
  font-size: 24px;
  margin-top: 2px;
}

.location-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.location-address {
  font-size: 14px;
  color: #606266;
  margin-bottom: 2px;
}

.location-coords {
  font-size: 12px;
  color: #909399;
}

@media (max-width: 768px) {
  .map-container {
    height: 300px;
  }
  
  .selected-location {
    flex-direction: column;
    gap: 12px;
  }
  
  .selected-location .el-button {
    width: 100%;
  }
}
</style>

