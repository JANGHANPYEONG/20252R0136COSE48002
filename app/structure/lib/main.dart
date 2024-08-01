import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:structure/config/user_router.dart';
import 'package:structure/dataSource/local_data_source.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/model/user_model.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: '.env');
  await Firebase.initializeApp();
  await initializeDateFormatting();

  await checkAutoLogin();
  runApp(const DeepPlantApp());
}

/// auto.json에 자동 로그인이 설정됐으면 자동으로 로그인
Future<void> checkAutoLogin() async {
  dynamic response = await LocalDataSource.getLocalData('auto.json');

  if (response != null) {
    Map<String, dynamic> data = response;

    if (data['auto'] != null) {
      // 로그인 진행
      if (await saveUserInfo(data['auto'])) {
        userModel.auto = true;
      }
    }
  }
}

/// 유저 정보 저장
Future<bool> saveUserInfo(String userId) async {
  // 로그인 API 호출
  try {
    // 유저 정보 가져오기 시도
    dynamic userInfo = await RemoteDataSource.login(userId)
        .timeout(const Duration(seconds: 10));
    if (userInfo is Map<String, dynamic>) {
      // 200 OK
      // 데이터 fetch
      userModel.fromJson(userInfo);
      // 육류 정보 생성자 id 저장
      meatModel.userId = userModel.userId;
      return true;
    } else {
      return false;
    }
  } catch (e) {
    return false;
  }
}

MeatModel meatModel = MeatModel();
UserModel userModel = UserModel();

// 라우팅
final _router = UserRouter.getRouter(meatModel, userModel);

class DeepPlantApp extends StatelessWidget {
  const DeepPlantApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ScreenUtilInit(
      designSize: const Size(720, 1280),
      child: MaterialApp.router(
        theme: ThemeData(
          fontFamily: 'Pretendard',
          scaffoldBackgroundColor: Colors.white,
        ),
        debugShowCheckedModeBanner: false,
        title: 'DeepPlant-demo',
        routerConfig: _router,
      ),
    );
  }
}
