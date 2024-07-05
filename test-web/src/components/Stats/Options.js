export const speciesOptions = [
  { value: 'cow', label: '소' },
  { value: 'pig', label: '돼지' },
];

export const primalOptions = {
  cow: [
    { value: 'tenderloin', label: '안심' },
    { value: 'sirloin', label: '등심' },
    { value: 'striploin', label: '채끝' },
    { value: 'chuck', label: '목심' },
    { value: 'blade', label: '앞다리' },
    { value: 'round', label: '우둔' },
    { value: 'bottom_round', label: '설도' },
    { value: 'brisket', label: '양지' },
    { value: 'shank', label: '사태' },
    { value: 'rib', label: '갈비' },
  ],
  pig: [
    { value: 'tenderloin', label: '안심' },
    { value: 'loin', label: '등심' },
    { value: 'boston_shoulder', label: '목심' },
    { value: 'picinc_shoulder', label: '앞다리' },
    { value: 'spare_ribs', label: '갈비' },
    { value: 'belly', label: '삼겹살' },
    { value: 'ham', label: '뒷다리' },
  ],
};

export const secondaryOptions = {
  cow: {
    tenderloin: [{ value: 'tenderloin', label: '안심살' }],
    sirloin: [
      { value: 'chuck_roll', label: '윗등심' },
      { value: 'ribeye_roll', label: '꽃등심' },
      { value: 'lower_sirloin', label: '아래등심' },
      { value: 'chuck_flap_tail', label: '살치살' },
    ],
    striploin: [{ value: 'strip_loin', label: '채끝살' }],
    chuck: [{ value: 'chuck', label: '목심살' }],
    blade: [
      { value: 'chuck_tender', label: '꾸리살' },
      { value: 'top_blade_muscle', label: '부채살' },
      { value: 'blade', label: '앞다리살' },
      { value: 'blade_meat', label: '갈비덧살' },
      { value: 'top_blade_meat', label: '부채덮개살' },
    ],
    round: [
      { value: 'inside_round', label: '우둔살' },
      { value: 'eye_of_round', label: '홍두깨살' },
    ],
    bottom_round: [
      { value: 'rump_round', label: '보섭살' },
      { value: 'top_sirloin', label: '설깃살' },
      { value: 'top_sirloin_cap', label: '설깃머리살' },
      { value: 'knuckle', label: '도가니살' },
      { value: 'tri_tip', label: '삼각살' },
    ],
    brisket: [
      { value: 'brisket', label: '양지머리' },
      { value: 'brisket_point', label: '차돌박이' },
      { value: 'plate', label: '업진살' },
      { value: 'inside_skirt', label: '업진안살' },
      { value: 'flank', label: '치마양지' },
      { value: 'flap_meat', label: '치마살' },
      { value: 'apron', label: '앞치마살' },
    ],
    shank: [
      { value: 'fore_shank', label: '앞사태' },
      { value: 'hind_shank', label: '뒷사태' },
      { value: 'heel_muscle', label: '뭉치사태' },
    ],
    rib: [
      { value: 'chuck_short_rib', label: '본갈비' },
      { value: 'boneless_short_rib', label: '꽃갈비' },
      { value: 'short_rib', label: '참갈비' },
      { value: 'interconstal', label: '갈빗살' },
      { value: 'tirmmed_rib', label: '마구리' },
      { value: 'hanging_tender', label: '토시살' },
      { value: 'outside_skirt', label: '안창살' },
      { value: 'neck_chain', label: '제비추리' },
    ],
  },
  pig: {
    tenderloin: [{ value: 'tenderloin', label: '안심살' }],
    loin: [
      { value: 'loin', label: '등실살' },
      { value: 'sirloin', label: '등심덧살' },
    ],
    boston_shoulder: [{ value: 'boston_shoulder', label: '목심살' }],
    picinc_shoulder: [
      { value: 'picnic_shoulder', label: '앞다리살' },
      { value: 'foreshank', label: '앞사태살' },
      { value: 'pork_jowl', label: '항정살' },
      { value: 'chuck_tender', label: '꾸리살' },
      { value: 'top_blade_muscle', label: '부채살' },
      { value: 'spatula_meat', label: '주걱살' },
    ],
    spare_ribs: [
      { value: 'rib', label: '갈비' },
      { value: 'ribs', label: '갈비살' },
      { value: 'tirmmed_rib', label: '마구리' },
    ],
    belly: [
      { value: 'belly', label: '삼겹살' },
      { value: 'skirt_meat', label: '갈매기살' },
      { value: 'back_rib', label: '등갈비' },
      { value: 'hanging_tender', label: '토시살' },
      { value: 'odol_belly', label: '오돌삼겹살' },
    ],
    ham: [
      { value: 'buttok', label: '볼기살' },
      { value: 'top_sirloin', label: '설깃살' },
      { value: 'knuckle', label: '도가니살' },
      { value: 'eye_of_round', label: '홍두께살' },
      { value: 'rump_round', label: '보섭살' },
      { value: 'hind_shank', label: '뒷사태살' },
    ],
  },
};
