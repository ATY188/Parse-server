/**
 * n8n 批次處理腳本
 * 用途：批次解析 n8n 產出的文章列表
 * 
 * 使用方式：
 * node n8n-batch-parser.js input.json output.json
 * 
 * 輸入格式 (input.json)：
 * [
 *   {"url": "https://example.com/article1", "id": "001"},
 *   {"url": "https://example.com/article2", "id": "002"}
 * ]
 */

import { readFile, writeFile } from 'fs/promises';
import { existsSync } from 'fs';

const API_URL = process.env.PARSER_API_URL || 'http://localhost:3000/api/parse';
const DELAY_MS = parseInt(process.env.DELAY_MS) || 2000; // 每個請求間隔（毫秒）
const MAX_RETRIES = parseInt(process.env.MAX_RETRIES) || 3; // 最大重試次數

console.log('📋 n8n 批次文章解析器');
console.log('==================================');
console.log(`🔗 API 端點: ${API_URL}`);
console.log(`⏱️  請求間隔: ${DELAY_MS}ms`);
console.log(`🔄 最大重試: ${MAX_RETRIES} 次\n`);

// 延遲函數
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// 解析單一文章
async function parseArticle(articleData, retryCount = 0) {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: articleData.url })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    
    if (result.success) {
      return {
        ...articleData,
        success: true,
        parsed_data: {
          title: result.data.title,
          author: result.data.author,
          date_published: result.data.date_published,
          content: result.data.content,
          excerpt: result.data.excerpt,
          word_count: result.data.word_count,
          lead_image_url: result.data.lead_image_url,
          domain: result.data.domain
        },
        parsed_at: new Date().toISOString()
      };
    } else {
      throw new Error('解析失敗');
    }
    
  } catch (error) {
    console.error(`❌ 解析失敗 (第 ${retryCount + 1} 次): ${articleData.url}`);
    console.error(`   錯誤: ${error.message}`);
    
    // 重試邏輯
    if (retryCount < MAX_RETRIES) {
      console.log(`   ⏳ 等待 ${DELAY_MS * 2}ms 後重試...`);
      await delay(DELAY_MS * 2);
      return parseArticle(articleData, retryCount + 1);
    }
    
    return {
      ...articleData,
      success: false,
      error: error.message,
      failed_at: new Date().toISOString()
    };
  }
}

// 主要批次處理函數
async function batchParse(inputFile, outputFile) {
  try {
    // 讀取輸入檔案
    if (!existsSync(inputFile)) {
      console.error(`❌ 找不到輸入檔案: ${inputFile}`);
      process.exit(1);
    }

    const inputData = JSON.parse(await readFile(inputFile, 'utf-8'));
    
    if (!Array.isArray(inputData)) {
      console.error('❌ 輸入檔案格式錯誤：必須是陣列');
      process.exit(1);
    }

    console.log(`📥 載入 ${inputData.length} 篇文章待解析\n`);

    const results = [];
    let successCount = 0;
    let failCount = 0;

    // 逐一處理每篇文章
    for (let i = 0; i < inputData.length; i++) {
      const article = inputData[i];
      const progress = `[${i + 1}/${inputData.length}]`;
      
      console.log(`${progress} 🔍 解析中: ${article.url}`);
      
      const result = await parseArticle(article);
      results.push(result);
      
      if (result.success) {
        successCount++;
        console.log(`${progress} ✅ 成功: ${result.parsed_data.title || '無標題'}`);
        console.log(`${progress}    字數: ${result.parsed_data.word_count || 0}, 作者: ${result.parsed_data.author || '未知'}`);
      } else {
        failCount++;
        console.log(`${progress} ❌ 失敗`);
      }
      
      // 避免請求過快（最後一個不需要延遲）
      if (i < inputData.length - 1) {
        await delay(DELAY_MS);
      }
      
      console.log(''); // 空行分隔
    }

    // 儲存結果
    await writeFile(outputFile, JSON.stringify(results, null, 2), 'utf-8');
    
    console.log('==================================');
    console.log('✨ 批次處理完成！');
    console.log(`📊 統計資訊:`);
    console.log(`   總計: ${inputData.length} 篇`);
    console.log(`   成功: ${successCount} 篇 (${(successCount/inputData.length*100).toFixed(1)}%)`);
    console.log(`   失敗: ${failCount} 篇 (${(failCount/inputData.length*100).toFixed(1)}%)`);
    console.log(`\n💾 結果已儲存至: ${outputFile}`);
    
    // 如果有失敗的項目，另外儲存失敗清單
    if (failCount > 0) {
      const failedItems = results.filter(r => !r.success);
      const failedFile = outputFile.replace('.json', '-failed.json');
      await writeFile(failedFile, JSON.stringify(failedItems, null, 2), 'utf-8');
      console.log(`⚠️  失敗項目已儲存至: ${failedFile}`);
    }
    
  } catch (error) {
    console.error('\n❌ 批次處理發生錯誤:', error.message);
    process.exit(1);
  }
}

// 主程式
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.log('使用方式：');
    console.log('  node n8n-batch-parser.js <輸入檔案.json> <輸出檔案.json>');
    console.log('');
    console.log('範例：');
    console.log('  node n8n-batch-parser.js articles.json results.json');
    console.log('');
    console.log('環境變數：');
    console.log('  PARSER_API_URL - Parser API 位址（預設: http://localhost:3000/api/parse）');
    console.log('  DELAY_MS - 請求間隔毫秒數（預設: 2000）');
    console.log('  MAX_RETRIES - 最大重試次數（預設: 3）');
    console.log('');
    console.log('輸入檔案格式：');
    console.log('  [');
    console.log('    {"url": "https://example.com/article1", "id": "001"},');
    console.log('    {"url": "https://example.com/article2", "id": "002"}');
    console.log('  ]');
    process.exit(1);
  }

  const [inputFile, outputFile] = args;
  await batchParse(inputFile, outputFile);
}

main();

