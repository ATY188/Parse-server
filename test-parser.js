/**
 * 測試腳本 - 用於測試 Parser API
 * 使用方式：node test-parser.js [URL]
 */

const testUrl = process.argv[2] || 'https://www.bbc.com/news';
const apiUrl = 'http://localhost:3000/api/parse';

console.log('🧪 開始測試 Parser API...\n');
console.log(`📰 目標 URL: ${testUrl}`);
console.log(`🔗 API 端點: ${apiUrl}\n`);

async function testParser() {
  try {
    console.log('⏳ 正在解析網頁...');
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: testUrl })
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ API 錯誤:', error);
      return;
    }

    const result = await response.json();
    
    console.log('\n✅ 解析成功！\n');
    console.log('📋 解析結果：');
    console.log('=====================================');
    console.log(`📌 標題: ${result.data.title || '無'}`);
    console.log(`✍️  作者: ${result.data.author || '無'}`);
    console.log(`📅 發布日期: ${result.data.date_published || '無'}`);
    console.log(`🌐 網域: ${result.data.domain || '無'}`);
    console.log(`📝 字數: ${result.data.word_count || 0}`);
    console.log(`📄 總頁數: ${result.data.total_pages || 1}`);
    console.log(`\n💬 摘要:\n${result.data.excerpt || '無'}`);
    console.log(`\n🖼️  主圖片: ${result.data.lead_image_url || '無'}`);
    console.log('\n=====================================');
    
    // 顯示內容的前 200 個字元
    if (result.data.content) {
      const contentPreview = result.data.content
        .replace(/<[^>]*>/g, '') // 移除 HTML 標籤
        .substring(0, 200);
      console.log(`\n📖 內容預覽:\n${contentPreview}...\n`);
    }
    
    console.log('✨ 測試完成！');
    
  } catch (error) {
    console.error('\n❌ 測試失敗:', error.message);
    console.log('\n💡 提示：');
    console.log('1. 確認伺服器已啟動：npm start');
    console.log('2. 確認網路連線正常');
    console.log('3. 確認目標 URL 可訪問\n');
  }
}

testParser();

