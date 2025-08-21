export const TIME_ZONE = 9 * 60 * 60 * 1000;

// ==================== 서버 API 설정 ====================
// 사용할 서버 주소를 아래에서 선택하세요

// 로컬 개발 서버 (로컬 테스트용)
export const apiIP = 'localhost:8080';

// Ubuntu AWS 서버 (운영 환경) - 서버 실행 후 사용
// export const apiIP = '172.31.6.111:8080';

// 기타 서버 (필요에 따라 추가)
// export const apiIP = 'your-server-ip:port';

// ==================== 스토리지 설정 ====================
// 파일 업로드 방식 선택

export const STORAGE_CONFIG = {
  // 업로드 방식: 'server' | 's3-direct' | 's3-presigned'
  uploadMethod: 'server',
  
  // 서버 업로드 방식 설정 (현재 사용 중)
  server: {
    endpoint: `/meat/add/upload/data`,
    basePath: './uploads', // 로컬 테스트용 (Ubuntu: /home/ubuntu/2025-Deeplant-Dev/database)
    csvPath: 'label',
    imagePath: 'image'
  },
  
  // S3 직접 업로드 설정 (AWS SDK 사용)
  s3Direct: {
    bucketName: 'your-bucket-name',
    region: 'ap-northeast-2',
    accessKeyId: '', // 환경변수나 IAM Role 사용 권장
    secretAccessKey: '', // 환경변수나 IAM Role 사용 권장
    csvFolder: 'data/csv/',
    imageFolder: 'data/images/'
  },
  
  // S3 Presigned URL 방식 설정
  s3Presigned: {
    presignedUrlEndpoint: '/api/s3/presigned-url',
    bucketName: 'your-bucket-name',
    csvFolder: 'data/csv/',
    imageFolder: 'data/images/'
  }
};