import React, { useState, useRef } from 'react';
import { Box, Button, Typography, CircularProgress } from '@mui/material';
import * as XLSX from 'xlsx';
import style from './style/dashboardstyle';
import DataListWithURL from '../components/DataListWithURL';

const navy = '#0F3659';

const DataRegister = () => {
    const [columns, setColumns] = useState([]);
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);

    const fileInputRef = useRef(null);
    const imageInputRef = useRef(null);
    const serialInputRef = useRef(null);

    const handleLoadClick = () => fileInputRef.current?.click();
    const handleImageClick = () => imageInputRef.current?.click();
    const handleSerialClick = () => serialInputRef.current?.click();

    const handleRegister = async () => {
        try {
            setLoading(true);
            await fetch('/api/data/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data }),
            });
            alert('데이터 등록 성공!');
            setColumns([]);
            setData([]);
        } catch (err) {
            console.error(err);
            alert('데이터 등록에 실패했습니다.');
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        setLoading(true);
        const reader = new FileReader();
        reader.onload = (evt) => {
            const wb = XLSX.read(evt.target.result, { type: 'array' });
            const sheet = wb.Sheets[wb.SheetNames[0]];
            const rowsArray = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });
            if (!rowsArray.length) {
                setColumns([]);
                setData([]);
                setLoading(false);
                return;
            }
            // 1행은 헤더, 빈 문자열 컬럼 제거
            const origHeader = rowsArray[1].map(String);
            const validIdx = origHeader
                .map((h, i) => ({ h: h.trim(), i }))
                .filter(({ h }) => h !== '')
                .map(({ i }) => i);
            const filteredHeaders = validIdx.map((i) => origHeader[i]);

            const dataRows = rowsArray.slice(2).filter((r) => r.some((c) => c !== ''));
            const mapped = dataRows.map((rowArr) => {
                const obj = {};
                validIdx.forEach((i, idx) => {
                    obj[filteredHeaders[idx]] = rowArr[i];
                });
                return obj;
            });

            setColumns(filteredHeaders);
            setData(mapped);
            setLoading(false);
        };
        reader.readAsArrayBuffer(file);
        e.target.value = null;
    };

    const handleImageChange = (e) => {
        const files = Array.from(e.target.files);
        // 이름에서 (index) 추출
        const mapByIndex = files.reduce((m, f) => {
            const match = f.name.match(/\((\d+)\)/);
            if (match) {
                m[match[1]] = {
                    name: f.name,
                    url: URL.createObjectURL(f),
                };
            }
            return m;
        }, {});
        const col = '이미지 파일명';
        if (!columns.includes(col)) setColumns((c) => [...c, col]);

        const key = columns[0];
        setData((d) =>
            d.map((row) => ({
                ...row,
                [col]: mapByIndex[row[key]]?.name || '',
                이미지URL: mapByIndex[row[key]]?.url || '',
            }))
        );
        e.target.value = null;
    };

    const handleSerialChange = (e) => {
        const files = Array.from(e.target.files);
        // 이름에서 _index. 또는 (index) 추출
        const mapByIndex = files.reduce((m, f) => {
            let match = f.name.match(/_(\d+)\./) || f.name.match(/\((\d+)\)/);
            if (match) {
                m[match[1]] = {
                    name: f.name,
                    url: URL.createObjectURL(f),
                };
            }
            return m;
        }, {});
        const col = '일련번호 파일명';
        if (!columns.includes(col)) setColumns((c) => [...c, col]);

        const key = columns[0];
        setData((d) =>
            d.map((row) => ({
                ...row,
                [col]: mapByIndex[row[key]]?.name || '',
                일련번호URL: mapByIndex[row[key]]?.url || '',
            }))
        );
        e.target.value = null;
    };

    return (
        <div
            style={{
                overflow: 'auto',
                width: '100%',
                marginTop: '100px',
                height: '100%',
                paddingLeft: '30px',
                paddingRight: '20px',
            }}
        >
            <Box
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    minWidth: '634px',
                }}
            >
                <span
                    style={{ color: `${navy}`, fontSize: '30px', fontWeight: '600' }}
                >
                    데이터 등록
                </span>
            </Box>

            {/* 숨겨진 입력들 */}
            <input
                type="file"
                accept=".xlsx"
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={handleFileChange}
            />
            <input
                type="file"
                accept="image/*"
                webkitdirectory=""
                directory=""
                multiple
                ref={imageInputRef}
                style={{ display: 'none' }}
                onChange={handleImageChange}
            />
            <input
                type="file"
                accept="image/*"
                webkitdirectory=""
                directory=""
                multiple
                ref={serialInputRef}
                style={{ display: 'none' }}
                onChange={handleSerialChange}
            />

            {/* 버튼 영역 */}
            <Box sx={{ ...style.fixedTab, display: 'flex', alignItems: 'center', gap: 2, mb: 4 }}>
                <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                        variant="contained"
                        onClick={handleLoadClick}
                        disabled={loading}
                        sx={{ backgroundColor: navy, '&:hover': { backgroundColor: '#0a2a4a' } }}
                    >
                        {loading ? <CircularProgress size={20} color="inherit" /> : '데이터 불러오기'}
                    </Button>
                    <Button
                        variant="contained"
                        onClick={handleImageClick}
                        disabled={loading}
                        sx={{ backgroundColor: navy, '&:hover': { backgroundColor: '#0a2a4a' } }}
                    >
                        사진 불러오기
                    </Button>
                    <Button
                        variant="contained"
                        onClick={handleSerialClick}
                        disabled={loading}
                        sx={{ backgroundColor: navy, '&:hover': { backgroundColor: '#0a2a4a' } }}
                    >
                        일련번호 불러오기
                    </Button>
                </Box>
                <Button
                    variant="contained"
                    onClick={handleRegister}
                    disabled={!data.length || loading}
                    sx={{ marginLeft: 'auto', backgroundColor: navy, '&:hover': { backgroundColor: '#0a2a4a' } }}
                >
                    {loading ? <CircularProgress size={20} color="inherit" /> : '데이터 등록'}
                </Button>
            </Box>

            <DataListWithURL title="미리보기" columns={columns} data={data} />
        </div>
    );
};

export default DataRegister;