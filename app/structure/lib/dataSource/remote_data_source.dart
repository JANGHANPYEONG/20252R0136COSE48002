//
//
// remote_data_source.
//
//

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import 'package:xml2json/xml2json.dart';

class RemoteDataSource {
  static String baseUrl = dotenv.env['API_URL']!;

  /* 사용자 관련 API */
  /// 유저 회원가입 (POST)
  ///
  /// 입력한 정보들 토대로 사용자 정보 DB에 생성하는 함수
  ///
  /// 전송 데이터 : userId, name, homeAddr, company, jobTitle, type, alarm
  ///
  /// Status code : 200, 400
  static Future<dynamic> signUp(String jsonData) async {
    dynamic response = await _postApi('user/register', jsonData);
    return response;
  }

  /// 유저 중복검사 (GET)
  ///
  /// 회원가입하려는 userId가 중복되는지 확인하는 함수
  ///
  /// isDuplicate로 중복 여부 확인
  ///
  /// Status code : 200
  static Future<dynamic> dupliCheck(String userId) async {
    dynamic response = await _getApi('user/duplicate-check?userId=$userId');
    return response;
  }

  /// 유저 로그인 (GET)
  ///
  /// 로그인시 입력한 userId를 토대로 사용자 정보를 불러오는 함수
  ///
  /// 받아오는 데이터 : userId, name, homeAddr, company, jobTitle, type, alarm, createdAt
  ///
  /// Status code : 200, 400, 404
  static Future<dynamic> login(String userId) async {
    dynamic response = await _getApi('user/login?userId=$userId');
    return response;
  }

  /// 유저 업데이트 (POST)
  ///
  /// 유저 정보 수정 후 DB에 반영하는 함수
  ///
  /// 전송 데이터 : userId, name, homeAddr, company, jobTitle, alarm, type
  ///
  /// Status code : 200, 400
  static Future<dynamic> updateUser(String jsonData) async {
    dynamic response = await _patchApi('user/update', jsonData);
    return response;
  }

  /// 유저 회원 탈퇴 (GET)
  ///
  /// 로그인된 사용자를 DB에서 삭제하는 함수
  ///
  /// Status code : 200, 401
  static Future<dynamic> deleteUser(String userId) async {
    dynamic response = await _deleteApi('user/delete?userId=$userId');
    return response;
  }

  /* 육류 관련 API */
  /// 모든 고기의 데이터 조회 (GET)
  ///
  /// 데이터 관리 - 일반 데이터 승인에서 사용하는 함수.
  ///
  /// 전체 데이터 조회:
  /// <br /> Offset, count - null
  /// <br /> specieValue - 전체
  /// <br /> start - 1970-01-01T00:00:00
  /// <br /> end - 현재 시간
  ///
  /// Status code : 200
  static Future<dynamic> getALLMeatData() async {
    String endPoint =
        'meat/get?specieValue=전체&start=1970-01-01T00:00:00&end=${DateTime.now().toIso8601String().substring(0, 19)}&offset=0&count=100';
    dynamic response = await _getApi(endPoint);
    return response;
  }

  /// 관리번호 육류 정보 조회 (GET)
  ///
  /// meatId를 전송하면 해당 meat에 대한 모든 정보를 불러오는 함수.
  ///
  /// 기본 육류 정보 + deepAgingInfo[]
  /// <br /> sensory_eval, heatedmeat_sensory_eval, probexpt_data, heated_probexpt_data
  ///
  /// Status code : 200, 400, 404
  static Future<dynamic> getMeatData(String meatId) async {
    dynamic response = await _getApi('meat/get/by-meat-id?meatId=$meatId');
    return response;
  }

  /// 승인된 관리번호 검색 (GET)
  ///
  /// 데이터 관리 - 추가 정보 입력에서 사용하는 함수.
  /// <br /> 추가정보 입력을 위한 statusType = 2(승인)인 육류 데이터만 불러오기
  ///
  /// 전체 데이터 조회:
  /// <br /> Offset, count - null
  /// <br /> specieValue - 전체
  /// <br /> start - 1970-01-01T00:00:00
  /// <br /> end - 현재 시간
  ///
  /// Status code : 200, 400
  static Future<dynamic> getConfirmedMeatData() async {
    dynamic response = await _getApi(
        'meat/get/by-status?statusType=2&specieValue=전체&start=1970-01-01T00:00:00&end=${DateTime.now().toIso8601String().substring(0, 19)}&offset=0&count=100');
    return response;
  }

  /// 유저가 등록한 관리번호 조회 (GET)
  static Future<dynamic> getUserMeatData(String userId) async {
    String endPoint =
        'meat/get/by-user-id?userId=$userId&specieValue=전체&start=1970-01-01T00:00:00&end=${DateTime.now().toIso8601String().substring(0, 19)}&offset=0&count=100';
    dynamic response = await _getApi(endPoint);
    return response;
  }

  /// 육류 정보 생성 (POST)
  ///
  /// null - 기본 육류 정보 생성
  /// <br /> sensory-eval - 관능평가 데이터 생성
  /// <br /> heatedmeat-eval - 가열육 관능평가 데이터 생성
  /// <br /> deep-aging-data - 딥에이징 데이터 생성
  /// <br /> probexpt-data - 실험실 데이터 생성
  ///
  /// Status code : 200, 400, 404
  static Future<dynamic> createMeatData(String? dest, String jsonData) async {
    String endPoint = 'meat/add/';
    if (dest != null) {
      endPoint = 'meat/add/$dest';
    }
    dynamic response = await _postApi(endPoint, jsonData);
    return response;
  }

  /// 육류 정보 업데이트 (PATCH)
  ///
  /// null - 기본 육류 정보 수정
  /// <br /> sensory-eval - 관능평가 데이터 수정
  /// <br /> heatedmeat-eval - 가열육 관능평가 데이터 수정
  /// <br /> deep-aging-data - 딥에이징 데이터 수정
  /// <br /> probexpt-data - 실험실 데이터 수정
  ///
  /// Status code : 200, 400, 404
  static Future<dynamic> patchMeatData(String? dest, String jsonData) async {
    String endPoint = 'meat/add/';
    if (dest != null) {
      endPoint = 'meat/add/$dest';
    }
    dynamic response = await _patchApi(endPoint, jsonData);
    return response;
  }

  /// 딥에이징 데이터 삭제 (GET)
  /// meatId, seqno에 해당하는 딥에이징 데이터 삭제
  /// 연결된 관능데이터, 가열육 관능데이터, 실험 데이터 등이 삭제됨
  // TODO : Patch로 변경, meatId 변경
  static Future<dynamic> deleteDeepAging(String meatId, int seqno) async {
    dynamic response =
        await _deleteApi('meat/delete/deep-aging?meatId=$meatId&seqno=$seqno');
    return response;
  }

  /// 육류 데이터 승인 (GET)
  ///
  /// meatId에 해당하는 육류 데이터를 승인
  static Future<dynamic> confirmMeatData(String meatId) async {
    dynamic response =
        await _patchApi('meat/update/confirm?meatId=$meatId', null);
    return response;
  }

  /// 육류 데이터 반려 (GET)
  ///
  /// meatId에 해당하는 육류 데이터를 반려
  static Future<dynamic> rejectMeatData(String meatId) async {
    dynamic response =
        await _patchApi('meat/update/reject?meatId=$meatId', null);
    return response;
  }

  /// category_info 테이블에서 종, 부위 데이터 불러오기 (GET)
  /// 소, 돼지 부위 정보 불러오기
  /// 종 - 대분할 - 소분할
  static Future<dynamic> getMeatSpecies() async {
    dynamic response = await _getApi('meat/get/default-data');
    return response;
  }

  /* 삭제 예정 */
  /// 일반 데이터와 연구 데이터 조회 (GET)
  // TODO : 삭제
  static Future<dynamic> getNormalResearchMeatData(String userType) async {
    String endPoint = 'meat/get/by-user-type?userType=$userType';
    dynamic response = await _getApi(endPoint);
    return response;
  }

  /// 유저 정보 조회 (GET)
  static Future<dynamic> getUserInfo(String userId) async {
    dynamic response = await _getApi('user/get?userId=$userId');
    return response;
  }

  /* GET, POST, DELETE */

  /// API POST
  ///
  /// 데이터 생성시 사용
  static Future<dynamic> _postApi(String endPoint, String jsonData) async {
    String apiUrl = '$baseUrl/$endPoint';
    Map<String, String> headers = {'Content-Type': 'application/json'};
    // String requestBody = jsonData;
    debugPrint('POST 요청: $endPoint');

    try {
      final response =
          await http.post(Uri.parse(apiUrl), headers: headers, body: jsonData);
      if (response.statusCode == 200) {
        debugPrint('POST 요청 성공');
      } else {
        debugPrint('POST 요청 실패: (${response.statusCode})${response.body}');
      }

      // 예외 처리를 위한 status code 반환
      return response.statusCode;
    } catch (e) {
      debugPrint('POST 요청 중 예외 발생: $e');
      return;
    }
  }

  /// API PATCH
  ///
  /// 데이터 일부 수정시 사용
  static Future<dynamic> _patchApi(String endPoint, String? jsonData) async {
    String apiUrl = '$baseUrl/$endPoint';
    Map<String, String> headers = {'Content-Type': 'application/json'};
    // String requestBody = jsonData;
    debugPrint('PATCH 요청: $endPoint');

    try {
      final response =
          await http.patch(Uri.parse(apiUrl), headers: headers, body: jsonData);
      if (response.statusCode == 200) {
        debugPrint('PATCH 요청 성공');
      } else {
        debugPrint('PATCH 요청 실패: (${response.statusCode})${response.body}');
      }

      return response.statusCode;
    } catch (e) {
      debugPrint('PATCH 요청 중 예외 발생: $e');
      return;
    }
  }

  /// API GET
  ///
  /// 데이터 받아올 때 사용
  static Future<dynamic> _getApi(String endPoint) async {
    String apiUrl = '$baseUrl/$endPoint';
    debugPrint('GET 요청: $endPoint');

    try {
      final response = await http.get(Uri.parse(apiUrl));

      if (response.statusCode == 200) {
        debugPrint('GET 요청 성공');
        return jsonDecode(response.body);
      } else {
        debugPrint('GET 요청 실패: (${response.statusCode})${response.body}');
        return response;
      }
    } catch (e) {
      debugPrint('GET 요청 중 예외 발생: $e');
      return;
    }
  }

  /// API DELETE
  ///
  /// 데이터 삭제시 사용
  static Future<dynamic> _deleteApi(String endPoint) async {
    String apiUrl = '$baseUrl/$endPoint';
    debugPrint('DELETE 요청: $endPoint');

    try {
      final response = await http.delete(Uri.parse(apiUrl));

      if (response.statusCode == 200) {
        debugPrint('DELETE 요청 성공');
      } else {
        debugPrint('DELETE 요청 실패: (${response.statusCode})${response.body}');
      }

      return response.statusCode;
    } catch (e) {
      debugPrint('DELETE 요청 중 예외 발생: $e');
      return;
    }
  }

  /// 육류 이력관리 정보 (GET)
  ///
  /// dotenv TRACEAPI
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
        debugPrint('${response.statusCode}');
        return;
      }
    } catch (e) {
      debugPrint('error');
      return;
    }
  }
}
