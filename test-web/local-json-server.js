const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const port = 3001;

// CORS 설정
app.use(cors());
app.use(express.json({ limit: '50mb' }));

// result 폴더 경로
const resultPath = path.join(__dirname, 'test-data', 'result');

// result 폴더가 없으면 생성
if (!fs.existsSync(resultPath)) {
  fs.mkdirSync(resultPath, { recursive: true });
  console.log('result 폴더가 생성되었습니다:', resultPath);
}

// JSON 파일 저장 API (여러 파일 지원, result 디렉토리에 직접 저장)
app.post('/api/save-multiple-json', async (req, res) => {
  try {
    const { files } = req.body;
    
    if (!files || !Array.isArray(files)) {
      return res.status(400).json({ 
        error: '잘못된 요청입니다. files 배열이 필요합니다.' 
      });
    }

    const savedFiles = [];
    
    for (const fileData of files) {
      const { fileName, content } = fileData;
      
      if (!fileName || !content) {
        console.warn('파일명 또는 내용이 누락된 파일을 건너뜁니다:', fileData);
        continue;
      }

      // result 디렉토리에 직접 저장
      const filePath = path.join(resultPath, fileName);
      
      // JSON 파일 저장
      fs.writeFileSync(filePath, content, 'utf8');
      
      savedFiles.push({
        fileName: fileName,
        filePath: filePath,
        size: content.length
      });
      
      console.log(`JSON 파일 저장됨: ${fileName} (크기: ${content.length} bytes)`);
    }

    res.json({
      success: true,
      message: `${savedFiles.length}개의 JSON 파일이 저장되었습니다.`,
      savedFiles: savedFiles,
      targetPath: resultPath
    });

  } catch (error) {
    console.error('JSON 파일 저장 오류:', error);
    res.status(500).json({ 
      error: '파일 저장 중 오류가 발생했습니다.',
      details: error.message 
    });
  }
});

// 단일 JSON 파일 저장 API (기존 호환성 유지)
app.post('/api/save-json', async (req, res) => {
  try {
    const { fileName, content } = req.body;
    
    if (!fileName || !content) {
      return res.status(400).json({ 
        error: '파일명과 내용이 필요합니다.' 
      });
    }

    const filePath = path.join(resultPath, fileName);
    
    // JSON 파일 저장
    fs.writeFileSync(filePath, content, 'utf8');
    
    console.log(`JSON 파일 저장됨: ${fileName} (크기: ${content.length} bytes)`);

    res.json({
      success: true,
      message: 'JSON 파일이 저장되었습니다.',
      filePath: filePath
    });

  } catch (error) {
    console.error('JSON 파일 저장 오류:', error);
    res.status(500).json({ 
      error: '파일 저장 중 오류가 발생했습니다.',
      details: error.message 
    });
  }
});

// 저장된 파일 목록 조회 API
app.get('/api/saved-files', (req, res) => {
  try {
    const files = fs.readdirSync(resultPath)
      .filter(file => file.endsWith('.json'))
      .map(file => {
        const filePath = path.join(resultPath, file);
        const stats = fs.statSync(filePath);
        return {
          fileName: file,
          size: stats.size,
          created: stats.birthtime,
          modified: stats.mtime
        };
      });

    res.json({
      success: true,
      files: files,
      totalCount: files.length,
      resultPath: resultPath
    });

  } catch (error) {
    console.error('파일 목록 조회 오류:', error);
    res.status(500).json({ 
      error: '파일 목록 조회 중 오류가 발생했습니다.',
      details: error.message 
    });
  }
});

// 서버 시작
app.listen(port, () => {
  console.log(`🚀 로컬 JSON 저장 서버가 시작되었습니다!`);
  console.log(`📁 저장 경로: ${resultPath}`);
  console.log(`🌐 서버 주소: http://localhost:${port}`);
  console.log(`📡 API 엔드포인트:`);
  console.log(`   - POST /api/save-multiple-json (여러 파일 저장)`);
  console.log(`   - POST /api/save-json (단일 파일 저장)`);
  console.log(`   - GET /api/saved-files (저장된 파일 목록)`);
});

// 서버 종료 시 정리
process.on('SIGINT', () => {
  console.log('\n서버를 종료합니다...');
  process.exit(0);
});

module.exports = app;