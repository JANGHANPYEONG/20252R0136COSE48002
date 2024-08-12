const getColor = (value) => {
    if (!value) {
      return '#ffffff';
    }
    const cattle = value.cattle;
    const pork = value.pork;
    const total = value.total;
    if (total === 0) {
      return '#ffffff';
    } else if (cattle === 0 && pork) {
      return pork > 40
        ? '#e91e63'
        : pork > 30
          ? '#ec407a'
          : pork > 20
            ? '#f06292'
            : pork > 10
              ? '#f48fb1'
              : '#f8bbd0';
    } else if (cattle && pork === 0) {
      return cattle > 40
        ? '#2196f3'
        : cattle > 30
          ? '#42a5f5'
          : cattle > 20
            ? '#64b5f6'
            : cattle > 10
              ? '#90caf9'
              : '#bbdefb';
    } else {
      return total > 40
        ? '#9c27b0'
        : total > 30
          ? '#ab47bc'
          : total > 20
            ? '#ba68c8'
            : total > 10
              ? '#ce93d8'
              : '#e1bee7';
    }
  };

  export default getColor