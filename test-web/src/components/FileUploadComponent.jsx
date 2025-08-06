import React, { useState } from 'react';
import addFileUpload from '../API/add/addFileUpload';

const FileUploadComponent = ({ meatId, userId }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileType, setFileType] = useState('image');
  const [description, setDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setUploadResult(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('파일을 선택해주세요.');
      return;
    }

    setUploading(true);
    
    try {
      const result = await addFileUpload(
        selectedFile,
        meatId,
        userId,
        fileType,
        description
      );

      setUploadResult(result);
      
      if (result.success) {
        alert('파일이 성공적으로 업로드되었습니다!');
        setSelectedFile(null);
        setDescription('');
      } else {
        alert(`업로드 실패: ${result.error}`);
      }
    } catch (error) {
      console.error('업로드 오류:', error);
      alert('업로드 중 오류가 발생했습니다.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h3>파일 업로드</h3>
      
      {/* 파일 타입 선택 */}
      <div style={{ marginBottom: '10px' }}>
        <label>파일 타입: </label>
        <select value={fileType} onChange={(e) => setFileType(e.target.value)}>
          <option value="image">이미지</option>
          <option value="csv">CSV 파일</option>
        </select>
      </div>

      {/* 파일 선택 */}
      <div style={{ marginBottom: '10px' }}>
        <label>파일 선택: </label>
        <input
          type="file"
          accept={fileType === 'image' ? 'image/*' : '.csv,text/csv'}
          onChange={handleFileChange}
        />
      </div>

      {/* 파일 설명 */}
      <div style={{ marginBottom: '10px' }}>
        <label>파일 설명: </label>
        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="파일에 대한 설명을 입력하세요 (선택사항)"
          style={{ width: '100%', padding: '5px' }}
        />
      </div>

      {/* 선택된 파일 정보 */}
      {selectedFile && (
        <div style={{ marginBottom: '10px', padding: '10px', backgroundColor: '#f5f5f5' }}>
          <p><strong>선택된 파일:</strong> {selectedFile.name}</p>
          <p><strong>파일 크기:</strong> {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
          <p><strong>파일 타입:</strong> {selectedFile.type}</p>
        </div>
      )}

      {/* 업로드 버튼 */}
      <div style={{ marginBottom: '10px' }}>
        <button
          onClick={handleUpload}
          disabled={!selectedFile || uploading}
          style={{ padding: '10px 20px' }}
        >
          {uploading ? '업로드 중...' : '파일 업로드'}
        </button>
      </div>

      {/* 업로드 결과 */}
      {uploadResult && (
        <div style={{ 
          padding: '10px', 
          marginTop: '10px',
          backgroundColor: uploadResult.success ? '#d4edda' : '#f8d7da',
          border: `1px solid ${uploadResult.success ? '#c3e6cb' : '#f5c6cb'}`,
          borderRadius: '5px'
        }}>
          {uploadResult.success ? (
            <div>
              <p style={{ color: '#155724', margin: 0 }}>
                ✅ 업로드 성공!
              </p>
              {uploadResult.data.filePath && (
                <p style={{ margin: '5px 0', fontSize: '12px' }}>
                  저장 경로: /mnt/data/{uploadResult.data.filePath}
                </p>
              )}
            </div>
          ) : (
            <p style={{ color: '#721c24', margin: 0 }}>
              ❌ 업로드 실패: {uploadResult.error}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default FileUploadComponent;
