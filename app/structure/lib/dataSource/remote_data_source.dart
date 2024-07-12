//
//
// remote_data_source.
//
//

import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import 'package:xml2json/xml2json.dart';

class RemoteDataSource {
  static String baseUrl = dotenv.env['API']!; // 로컬 서버

  /* 사용자 관련 API */
  /// 유저 회원가입 (POST)
  static Future<dynamic> signUp(String jsonData) async {
    dynamic response = await _postApi('user/register', jsonData);
    return response;
  }

  /// 유저 업데이트 (POST)
  static Future<dynamic> updateUser(String jsonData) async {
    dynamic response = await _postApi('user/update', jsonData);
    return response;
  }

  /// 유저 비밀번호 변경 (POST)
  static Future<dynamic> changeUserPw(String jsonData) async {
    dynamic response = await _postApi('user/update', jsonData);
    return response;
  }

  /// 유저 비밀번호 검사 (POST)
  static Future<dynamic> checkUserPw(String jsonData) async {
    dynamic response = await _postApi('user/pwd-check', jsonData);
    return response;
  }

  /// 유저 로그인 (GET)
  static Future<dynamic> signIn(String userId) async {
    dynamic response = await _getApi('user/login?userId=$userId');
    return response;
  }

  /// 유저 중복검사 (GET)
  static Future<dynamic> dupliCheck(String userId) async {
    dynamic response = await _getApi('user/duplicate-check?userId=$userId');
    return response;
  }

  /// 유저 회원 탈퇴 (GET)
  static Future<dynamic> deleteUser(String userId) async {
    dynamic response = await _getApi("user/delete?userId=$userId");
    return response;
  }

  /// 유저 정보 조회 (GET)
  static Future<dynamic> getUserInfo(String userId) async {
    dynamic response = await _getApi("user/get?userId=$userId");
    return response;
  }

  /* 육류 관련 API */
  /// 육류 정보 전송 (POST)
  static Future<dynamic> sendMeatData(String? dest, String jsonData) async {
    String endPoint = 'meat/add/';
    if (dest != null) {
      endPoint = 'meat/add/$dest';
    }
    dynamic response = await _postApi(endPoint, jsonData);
    return response;
  }

  /// 관리번호 육류 정보 조회 (GET)
  static Future<dynamic> getMeatData(String id) async {
    dynamic response = await _getApi('meat/get/by-id?id=$id');
    return response;
  }

  /// 딥에이징 데이터 삭제 (GET)
  static Future<dynamic> deleteDeepAging(String id, int seqno) async {
    dynamic response =
        await _deleteApi('meat/delete/deep-aging?id=$id&seqno=$seqno');
    return response;
  }

  /// 승인된 관리번호 검색
  static Future<dynamic> getConfirmedMeatData() async {
    dynamic response = await _getApi('meat/get/by-status?statusType=2');
    return response;
  }

  /// 유저가 등록한 관리번호 조회 (GET)
  static Future<dynamic> getUserMeatData(String userId) async {
    String endPoint = 'meat/get/by-user-id?userId=$userId';
    dynamic response = await _getApi(endPoint);
    return response;
  }

  /// 모든 고기의 데이터 조회 (GET)
  static Future<dynamic> getALLMeatData() async {
    String endPoint = 'meat/get';
    dynamic response = await _getApi(endPoint);
    return response;
  }

  /// 일반 데이터와 연구 데이터 조회 (GET)
  static Future<dynamic> getNormalResearchMeatData(String userType) async {
    String endPoint = 'meat/get/by-user-type?userType=$userType';
    dynamic response = await _getApi(endPoint);
    return response;
  }

  /// 육류 데이터 승인 (GET)
  static Future<dynamic> confirmMeatData(String meatId) async {
    dynamic response = await _getApi('meat/update/confirm?id=$meatId');
    return response;
  }

  /// 육류 데이터 반려 (GET)
  static Future<dynamic> rejectMeatData(String meatId) async {
    dynamic response = await _getApi('meat/update/reject?id=$meatId');
    return response;
  }

  /// category_info 테이블에서 종, 부위 데이터 불러오기 (GET)
  static Future<dynamic> getMeatSpecies() async {
    dynamic response = await _getApi('meat/get/default-data');
    return response;
  }

  /// API POST
  static Future<dynamic> _postApi(String endPoint, String jsonData) async {
    String apiUrl = '$baseUrl/$endPoint';
    Map<String, String> headers = {'Content-Type': 'application/json'};
    String requestBody = jsonData;

    try {
      final response = await http.post(Uri.parse(apiUrl),
          headers: headers, body: requestBody);
      if (response.statusCode == 200) {
        print('POST 요청 성공');
        return response.body;
      } else {
        print('POST 요청 실패: (${response.statusCode})${response.body}');
        return response.statusCode;
      }
    } catch (e) {
      print('POST 요청 중 예외 발생: $e');
      return;
    }
  }

  /// API GET
  static Future<dynamic> _getApi(String endPoint) async {
    String apiUrl = '$baseUrl/$endPoint';
    try {
      final response = await http.get(Uri.parse(apiUrl));

      if (response.statusCode == 200) {
        print('GET 요청 성공');
        return jsonDecode(response.body);
      } else {
        print('GET 요청 실패: (${response.statusCode})${response.body}');
        return;
      }
    } catch (e) {
      print('GET 요청 중 예외 발생: $e');
      return;
    }
  }

  static Future<dynamic> _deleteApi(String endPoint) async {
    String apiUrl = '$baseUrl/$endPoint';
    try {
      final response = await http.delete(Uri.parse(apiUrl));

      if (response.statusCode == 200) {
        print('Delete 요청 성공');
        return jsonDecode(response.body);
      } else {
        print('Delete 요청 실패: (${response.statusCode})${response.body}');
        return;
      }
    } catch (e) {
      print('Delete 요청 중 예외 발생: $e');
      return;
    }
  }

  /// 육류 이력관리 정보 (GET)
  static Future<dynamic> getMeatTraceData(String url) async {
    try {
      final response = await http.get(Uri.parse(url));

      if (response.statusCode == 200) {
        final body = utf8.decode(response.bodyBytes);
        final xml2JsonData = Xml2Json()..parse(body);
        final jsonData = xml2JsonData.toParker();

        final parsingData = jsonDecode(jsonData);

        return parsingData;
      } else {
        print(response.statusCode);
        return;
      }
    } catch (e) {
      print("error");
      return;
    }
  }
}
