import { STORAGE_CONFIG, apiIP } from '../../config';

/**
 * S3에 직접 파일 업로드 (AWS SDK 방식)
 * 사용하려면 먼저 AWS SDK 설치 필요: npm install aws-sdk
 */
export const uploadToS3Direct = async (data, columns, zipFile) => {
  try {
    // AWS SDK 동적 import (설치되어 있을 때만)
    const AWS = await import('aws-sdk');
    
    const s3Config = STORAGE_CONFIG.s3Direct;
    
    // S3 클라이언트 설정
    const s3 = new AWS.S3({
      accessKeyId: s3Config.accessKeyId,
      secretAccessKey: s3Config.secretAccessKey,
      region: s3Config.region
    });
    
    // CSV 데이터 생성
    const csvHeader = columns.join(',') + '\n';
    const csvRows = data.map(row => 
      columns.map(col => {
        const value = row[col] ?? '';
        if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    );
    const csvContent = csvHeader + csvRows.join('\n');
    
    // 파일명 생성 (타임스탬프 포함)
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const csvKey = `${s3Config.csvFolder}data_${timestamp}.csv`;
    const zipKey = `${s3Config.imageFolder}images_${timestamp}.zip`;
    
    // CSV 파일 업로드
    const csvUpload = await s3.upload({
      Bucket: s3Config.bucketName,
      Key: csvKey,
      Body: csvContent,
      ContentType: 'text/csv'
    }).promise();
    
    // ZIP 파일 업로드
    const zipUpload = await s3.upload({
      Bucket: s3Config.bucketName,
      Key: zipKey,
      Body: zipFile,
      ContentType: 'application/zip'
    }).promise();
    
    return {
      success: true,
      data: {
        csvUrl: csvUpload.Location,
        zipUrl: zipUpload.Location,
        csvKey: csvKey,
        zipKey: zipKey
      },
      message: 'S3에 파일이 성공적으로 업로드되었습니다.'
    };
    
  } catch (error) {
    console.error('S3 업로드 오류:', error);
    return {
      success: false,
      error: error.message,
      message: `S3 업로드 실패: ${error.message}`
    };
  }
};

/**
 * Presigned URL을 통한 S3 업로드
 */
export const uploadToS3Presigned = async (data, columns, zipFile) => {
  try {
    const s3Config = STORAGE_CONFIG.s3Presigned;
    
    // CSV 데이터 생성
    const csvHeader = columns.join(',') + '\n';
    const csvRows = data.map(row => 
      columns.map(col => {
        const value = row[col] ?? '';
        if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    );
    const csvContent = csvHeader + csvRows.join('\n');
    
    // 파일명 생성
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const csvFileName = `data_${timestamp}.csv`;
    const zipFileName = `images_${timestamp}.zip`;
    
    // 1. Presigned URL 요청
    const presignedResponse = await fetch(`http://${apiIP}${s3Config.presignedUrlEndpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        files: [
          {
            fileName: csvFileName,
            contentType: 'text/csv',
            folder: s3Config.csvFolder
          },
          {
            fileName: zipFileName,
            contentType: 'application/zip',
            folder: s3Config.imageFolder
          }
        ]
      })
    });
    
    if (!presignedResponse.ok) {
      throw new Error('Presigned URL 요청 실패');
    }
    
    const presignedData = await presignedResponse.json();
    const csvPresignedUrl = presignedData.urls[0];
    const zipPresignedUrl = presignedData.urls[1];
    
    // 2. CSV 파일 업로드
    const csvBlob = new Blob([csvContent], { type: 'text/csv' });
    const csvUploadResponse = await fetch(csvPresignedUrl, {
      method: 'PUT',
      body: csvBlob,
      headers: {
        'Content-Type': 'text/csv'
      }
    });
    
    if (!csvUploadResponse.ok) {
      throw new Error('CSV 파일 업로드 실패');
    }
    
    // 3. ZIP 파일 업로드
    const zipUploadResponse = await fetch(zipPresignedUrl, {
      method: 'PUT',
      body: zipFile,
      headers: {
        'Content-Type': 'application/zip'
      }
    });
    
    if (!zipUploadResponse.ok) {
      throw new Error('ZIP 파일 업로드 실패');
    }
    
    return {
      success: true,
      data: {
        csvUrl: csvPresignedUrl.split('?')[0], // 쿼리 파라미터 제거
        zipUrl: zipPresignedUrl.split('?')[0], // 쿼리 파라미터 제거
        csvKey: `${s3Config.csvFolder}${csvFileName}`,
        zipKey: `${s3Config.imageFolder}${zipFileName}`
      },
      message: 'S3에 파일이 성공적으로 업로드되었습니다.'
    };
    
  } catch (error) {
    console.error('S3 Presigned URL 업로드 오류:', error);
    return {
      success: false,
      error: error.message,
      message: `S3 업로드 실패: ${error.message}`
    };
  }
};

/**
 * 설정에 따라 적절한 업로드 방식을 선택하는 통합 함수
 */
export const uploadFiles = async (data, columns, zipFile, dataFormat = 'HSI') => {
  const method = STORAGE_CONFIG.uploadMethod;
  
  switch (method) {
    case 's3-direct':
      return await uploadToS3Direct(data, columns, zipFile, dataFormat);
    
    case 's3-presigned':
      return await uploadToS3Presigned(data, columns, zipFile, dataFormat);
    
    case 'server':
    default:
      // 기존 서버 업로드 방식 사용
      const { uploadDataToServer } = await import('./uploadDataToServer');
      return await uploadDataToServer(data, columns, zipFile, dataFormat);
  }
};

export default uploadFiles;
