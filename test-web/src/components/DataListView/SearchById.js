import React, { useState } from 'react';
import { apiIP } from '../../config';
import { HiOutlineSearch } from 'react-icons/hi';
import { TextField, IconButton, Box } from '@mui/material';
import { getByMeatId } from '../../API/get/getByMeatId';

function SearchById({ onDataFetch, onValueChange }) {
  const [meatId, setMeatId] = useState('');
  const [error, setError] = useState(false);

  const handleChange = (e) => {
    const { value } = e.target;
    // 정규식으로 영어/숫자만 허용
    const regex = /^[a-zA-Z0-9]*$/;
    if (regex.test(value)) {
      setMeatId(value);
      setError(false);
    } else {
      setMeatId(value);
      setError(true);
    }
  };

  const handleSearch = async () => {
    if (error || !meatId) return; // error가 있거나 id가 없으면 검색하지 않음
    try {
      const response = await getByMeatId(meatId)//getbymeatid api 호출
      const data = await response.json();
      onDataFetch(data);
      onValueChange('single');
    } catch (error) {
      console.error('Error fetching data:', error);
      onDataFetch(null); // 에러 발생 시 데이터 초기화
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1, // 간격을 추가하여 인풋과 버튼 사이에 여유 공간을 둡니다.
        backgroundColor: '#ffffff', // 배경색을 설정합니다.
        borderRadius: '4px', // 모서리를 둥글게 설정합니다.
        padding: '5px', // 안쪽 여백을 설정합니다.
      }}
    >
      <TextField
        value={meatId}
        onChange={handleChange}
        placeholder="ID"
        variant="outlined"
        size="small"
        error={error}
        helperText={error ? '영어와 숫자만 입력할 수 있습니다.' : ''}
        sx={{
          flex: 1, // 인풋이 가능한 한 넓게 차지하도록 설정합니다.
          backgroundColor: 'white', // 인풋의 배경색을 설정합니다.
          borderRadius: '4px', // 인풋의 모서리를 둥글게 설정합니다.
        }}
      />
      <IconButton
        onClick={handleSearch}
        color="primary"
        sx={{
          backgroundColor: '#115293', // 버튼의 배경색을 설정합니다.
          color: 'white', // 버튼 아이콘의 색상을 설정합니다.
          '&:hover': {
            backgroundColor: 'Navy', // 호버 시 버튼의 배경색을 설정합니다.
          },
        }}
      >
        <HiOutlineSearch />
      </IconButton>
    </Box>
  );
}

export default SearchById;
