// 상세 페이지에서 목록페이지로 이동 컴포넌트
const NavToList = (pageOffset, idParam) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', marginLeft: '10px' }}>
      <Link
        to={{ pathname: '/DataManage', search: `?pageOffset=${pageOffset}` }}
        style={{
          textDecorationLine: 'none',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <IconButton
          style={{
            color: `${navy}`,
            backgroundColor: 'white',
            border: `1px solid ${navy}`,
            borderRadius: '10px',
            marginRight: '10px',
          }}
        >
          <FaArrowLeft />
        </IconButton>
      </Link>
      <span
        style={{
          textDecoration: 'none',
          color: `${navy}`,
          fontSize: '30px',
          fontWeight: '600',
        }}
      >
        {idParam.id}
      </span>
    </div>
  );
};
export default NavToList;
