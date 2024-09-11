// 컬러팔레트 컴포넌트
import React from 'react';

const ColorPaletteMaker = ({ colors, showPercentage = false }) => {
  return (
    <div style={{ display: 'flex' }}>
      {colors.map((color, index) => (
        <div
          key={index}
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <div
            style={{
              width: '60px',
              height: '80px',
              backgroundColor: `rgb(${color[0].join(',')})`,
            }}
          />
          {/* Conditionally show the percentage */}
          {showPercentage && (
            <span style={{ marginTop: '5px' }}>
              {(color[1] * 100).toFixed(2)}
            </span>
          )}
        </div>
      ))}
    </div>
  );
};

export default ColorPaletteMaker;

/**
 아래와 같은 형식의 데이터에서 컬러팔레트 생성

 -> showPercentage = false
 proteinColorPalette: [
    [189, 89, 65],
    [182, 77, 57],
    [164, 65, 51],
    [146, 53, 43],
    [138, 51, 41],
  ], 

 -> showPercentage = true
  totalColorPalette: [
    [[189, 89, 65], 0.11738679846938775],
    [[182, 77, 57], 0.1253985969387755],
    [[164, 65, 51], 0.11888153698979592],
    [[146, 53, 43], 0.1129623724489796],
    [[138, 51, 41], 0.11090959821428571],
    [[214, 186, 191], 0.026486766581632654],
    [[183, 167, 175], 0.04338727678571429],
    [[212, 204, 217], 0.014449139030612245],
    [[214, 186, 191], 0.0262874681122449],
    [[212, 204, 217], 0.010901626275510204],
  ],
  */
