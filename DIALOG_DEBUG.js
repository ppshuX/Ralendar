// ====================================
// 📊 对话框表单样式调试脚本
// ====================================
// 
// 使用方法：
// 1. 打开 Ralendar 网站
// 2. 打开"编辑日程"或"添加日程"对话框
// 3. 按 F12 打开开发者工具
// 4. 切换到 Console（控制台）标签
// 5. 复制下面的代码，粘贴到控制台并按回车
//
// ====================================

console.clear();
console.log('====================================');
console.log('📊 对话框表单样式调试');
console.log('====================================\n');

// 查找对话框
const dialog = document.querySelector('.el-dialog');
if (!dialog) {
    console.error('❌ 未找到对话框！请先打开"编辑日程"或"添加日程"对话框。');
} else {
    console.log('✅ 找到对话框\n');
    
    // 查找第一个表单项
    const formItem = dialog.querySelector('.el-form-item');
    if (!formItem) {
        console.error('❌ 未找到表单项');
    } else {
        console.log('✅ 找到表单项\n');
        
        // 查找标签
        const label = formItem.querySelector('.el-form-item__label');
        if (label) {
            const labelStyles = window.getComputedStyle(label);
            console.log('📝 标签 (.el-form-item__label) 样式：');
            console.log('   width:', labelStyles.width);
            console.log('   padding-right:', labelStyles.paddingRight);
            console.log('   float:', labelStyles.float);
            console.log('   text-align:', labelStyles.textAlign);
            console.log('   font-size:', labelStyles.fontSize);
            console.log('   实际文字内容:', `"${label.textContent.trim()}"`);
            console.log('   实际占用空间:', label.offsetWidth + 'px\n');
        }
        
        // 查找内容区域
        const content = formItem.querySelector('.el-form-item__content');
        if (content) {
            const contentStyles = window.getComputedStyle(content);
            console.log('📦 内容区域 (.el-form-item__content) 样式：');
            console.log('   margin-left:', contentStyles.marginLeft);
            console.log('   width:', contentStyles.width);
            console.log('   实际占用空间:', content.offsetWidth + 'px\n');
        }
        
        // 计算实际间距
        if (label && content) {
            const labelRight = label.getBoundingClientRect().right;
            const contentLeft = content.getBoundingClientRect().left;
            const actualGap = contentLeft - labelRight;
            console.log('📏 实际测量：');
            console.log('   标签右边缘坐标:', labelRight.toFixed(2) + 'px');
            console.log('   内容左边缘坐标:', contentLeft.toFixed(2) + 'px');
            console.log('   ⚠️ 实际间距:', actualGap.toFixed(2) + 'px');
            console.log('');
        }
    }
    
    // 查找输入框
    const input = dialog.querySelector('.el-input');
    if (input) {
        const inputInner = input.querySelector('.el-input__inner');
        if (inputInner) {
            const inputStyles = window.getComputedStyle(inputInner);
            console.log('📝 输入框 (.el-input__inner) 样式：');
            console.log('   width:', inputStyles.width);
            console.log('   font-size:', inputStyles.fontSize);
            console.log('   padding:', inputStyles.padding);
            console.log('');
        }
    }
}

console.log('====================================');
console.log('💡 建议：');
console.log('如果实际间距太大，请截图并发送给开发者');
console.log('====================================');

