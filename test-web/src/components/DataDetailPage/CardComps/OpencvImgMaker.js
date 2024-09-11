import React from 'react';
import style from '../style/opencvimgmakerstyle';
import ColorPaletteMaker from './ColorPaletteMaker';

// OpenCV 이미지 생성 컴포넌트
const OpencvImgMaker = ({ data }) => {
  if (!data) return <div style={style.overlayNotExistWrapper}>Loading...</div>;

  return (
    <div
      style={{
        backgroundColor: 'white',
        padding: '20px',
        border: '1px solid #ccc',
        borderRadius: '5px',
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between',
        gap: '20px',
        boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)',
      }}
    >
      {/* 단면 이미지 */}
      {data.segmentImage && (
        <div>
          <div style={style.imgTitleWrapper}>단면 이미지</div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <img
              src={data.segmentImage}
              alt="Segmented Image"
              style={style.imgWrapper}
            />
          </div>
        </div>
      )}

      {/* 컬러팔레트 */}
      <div style={{ flex: 1 }}>
        <div style={{ marginBottom: '20px' }}>
          <div style={style.imgTitleWrapper}>단백질 컬러팔레트</div>
          <ColorPaletteMaker
            colors={data.proteinColorPalette.map((color) => [color])}
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <div style={style.imgTitleWrapper}>지방 컬러팔레트</div>
          <ColorPaletteMaker
            colors={data.fatColorPalette.map((color) => [color])}
          />
        </div>

        <div>
          <div style={style.imgTitleWrapper}>전체 컬러팔레트 (%)</div>
          {/* Use ColorPalette and pass the color and percentage */}
          <ColorPaletteMaker
            colors={data.totalColorPalette}
            showPercentage={true}
          />
        </div>
      </div>
    </div>
  );
};

export default OpencvImgMaker;
