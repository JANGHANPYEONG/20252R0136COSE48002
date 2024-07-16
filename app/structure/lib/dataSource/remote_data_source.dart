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
  static String baseUrl = dotenv.env['API']!;

  /* 사용자 관련 API */
  /// 유저 회원가입 (POST)
  /// 입력한 정보들 토대로 사용자 정보 DB에 생성하는 함수
  /// 전송 데이터 : userId, name, company, jobTitle, homeAddr alarm, type
  static Future<dynamic> signUp(String jsonData) async {
    dynamic response = await _postApi('user/register', jsonData);
    return response;
  }

  /// 유저 중복검사 (GET)
  /// 회원가입하려는 userId가 중복되는지 확인하는 함수
  /// null이 아니면 중복되지 않은 이메일
  static Future<dynamic> dupliCheck(String userId) async {
    dynamic response = await _getApi('user/duplicate-check?userId=$userId');
    return response;
  }

  /// 유저 로그인 (GET)
  /// 로그인시 입력한 userId를 토대로 사용자 정보를 불러오는 함수
  static Future<dynamic> login(String userId) async {
    dynamic response = await _getApi('user/login?userId=$userId');
    return response;
  }

  /// 유저 업데이트 (POST)
  /// 유저 정보 수정 후 DB에 반영하는 함수
  /// 전송 데이터 : userId, name, homeAddr, company, jobTitle, alarm, type
  // TODO : patch로 변경
  static Future<dynamic> updateUser(String jsonData) async {
    dynamic response = await _postApi('user/update', jsonData);
    return response;
  }

  /// 유저 회원 탈퇴 (GET)
  /// 로그인된 사용자를 DB에서 삭제하는 함수
  // TODO : delete로 변경
  static Future<dynamic> deleteUser(String userId) async {
    dynamic response = await _getApi('user/delete?userId=$userId');
    return response;
  }

  /* 육류 관련 API */
  /// 모든 고기의 데이터 조회 (GET)
  /// 일반데이터승인 - 전체 조회
  /// 전송 데이터 : offset, count, start, end, specieValue(전체, 소, 돼지)
  static Future<dynamic> getALLMeatData(int offset, int count, String start,
      String end, String specieValue) async {
    String endPoint =
        'meat/get?offset=$offset&count=$count&start=$start&end=$end&specieValue=$specieValue';
    dynamic response = await _getApi(endPoint);
    return response;
  }

  /// 관리번호 육류 정보 조회 (GET)
  /// meatId를 전송하면 해당 meat에 대한 모든 정보를 불러옴
  // TODO : by-meat-id로 변경
  static Future<dynamic> getMeatData(String id) async {
    dynamic response = await _getApi('meat/get/by-id?id=$id');
    return response;
  }

  /// 승인된 관리번호 검색
  /// 추가정보입력 - 전체 조회
  /// 추가정보 입력을 위한 statusType = 2(승인)인 육류 데이터만 불러오기
  /// TODO : offset, count, start, end, specieValue(전체, 소, 돼지)
  /// 전체 데이터 조회시 start에 1970-01-01T00:00:00Z 입력
  static Future<dynamic> getConfirmedMeatData() async {
    dynamic response = await _getApi('meat/get/by-status?statusType=2');
    return response;
  }

  /// 육류 정보 생성 (POST)
  /// null - 기본 육류 정보 생성
  /// sensory-eval - 관능평가 데이터 생성
  /// heatedmeat-eval - 가열육 관능평가 데이터 생성
  /// deep-aging-data - 딥에이징 데이터 생성
  /// probexpt-data - 실험실 데이터 생성
  // TODO : createMeatData로 이름 변경
  static Future<dynamic> sendMeatData(String? dest, String jsonData) async {
    String endPoint = 'meat/add/';
    if (dest != null) {
      endPoint = 'meat/add/$dest';
    }
    dynamic response = await _postApi(endPoint, jsonData);
    return response;
  }

  /// 육류 정보 업데이트 (PATCH)
  /// null - 기본 육류 정보 수정
  /// sensory-eval - 관능평가 데이터 수정
  /// heatedmeat-eval - 가열육 관능평가 데이터 수정
  /// deep-aging-data - 딥에이징 데이터 수정
  /// probexpt-data - 실험실 데이터 수정
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
  static Future<dynamic> deleteDeepAging(String id, int seqno) async {
    dynamic response =
        await _deleteApi('meat/delete/deep-aging?id=$id&seqno=$seqno');
    return response;
  }

  /// 육류 데이터 승인 (GET)
  /// meatId에 해당하는 육류 데이터를 승인
  // TODO : Patch 변경, meatId 변경
  static Future<dynamic> confirmMeatData(String meatId) async {
    dynamic response = await _getApi('meat/update/confirm?id=$meatId');
    return response;
  }

  /// 육류 데이터 반려 (GET)
  /// meatId에 해당하는 육류 데이터를 반려
  // TODO : Patch 변경, meatId 변경
  static Future<dynamic> rejectMeatData(String meatId) async {
    dynamic response = await _getApi('meat/update/reject?id=$meatId');
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
  /// 유저가 등록한 관리번호 조회 (GET)
  /// TODO : 삭제
  static Future<dynamic> getUserMeatData(String userId) async {
    String endPoint = 'meat/get/by-user-id?userId=$userId';
    dynamic response = await _getApi(endPoint);
    return response;
  }

  /// 일반 데이터와 연구 데이터 조회 (GET)
  // TODO : 삭제
  static Future<dynamic> getNormalResearchMeatData(String userType) async {
    String endPoint = 'meat/get/by-user-type?userType=$userType';
    dynamic response = await _getApi(endPoint);
    return response;
  }

  /// 유저 정보 조회 (GET)
  // TODO : 삭제
  static Future<dynamic> getUserInfo(String userId) async {
    dynamic response = await _getApi('user/get?userId=$userId');
    return response;
  }

  /* GET, POST, DELETE */

  /// API POST
  /// 데이터 생성시 사용
  static Future<dynamic> _postApi(String endPoint, String jsonData) async {
    String apiUrl = '$baseUrl/$endPoint';
    Map<String, String> headers = {'Content-Type': 'application/json'};
    String requestBody = jsonData;

    try {
      final response = await http.post(Uri.parse(apiUrl),
          headers: headers, body: requestBody);
      if (response.statusCode == 200) {
        debugPrint('POST 요청 성공: $endPoint');
        return response.body;
      } else {
        debugPrint(
            'POST 요청 실패: $endPoint (${response.statusCode})${response.body}');
        return response.statusCode;
      }
    } catch (e) {
      debugPrint('POST 요청 중 예외 발생: $e');
      return;
    }
  }

  /// API PATCH
  /// 데이터 일부 수정시 사용
  static Future<dynamic> _patchApi(String endPoint, String jsonData) async {
    String apiUrl = '$baseUrl/$endPoint';
    Map<String, String> headers = {'Content-Type': 'application/json'};
    String requestBody = jsonData;

    try {
      final response = await http.patch(Uri.parse(apiUrl),
          headers: headers, body: requestBody);
      if (response.statusCode == 200) {
        debugPrint('PATCH 요청 성공: $endPoint');
        return response.body;
      } else {
        debugPrint(
            'PATCH 요청 실패: $endPoint (${response.statusCode})${response.body}');
        return response.statusCode;
      }
    } catch (e) {
      debugPrint('PATCH 요청 중 예외 발생: $e');
      return;
    }
  }

  /// API GET
  /// 데이터 받아올 때 사용
  static Future<dynamic> _getApi(String endPoint) async {
    String apiUrl = '$baseUrl/$endPoint';
    try {
      final response = await http.get(Uri.parse(apiUrl));

      if (response.statusCode == 200) {
        debugPrint('GET 요청 성공: $endPoint');
        return jsonDecode(response.body);
      } else {
        debugPrint(
            'GET 요청 실패: $endPoint (${response.statusCode})${response.body}');
        return;
      }
    } catch (e) {
      debugPrint('GET 요청 중 예외 발생: $e');
      return;
    }
  }

  /// API DELETE
  /// 데이터 삭제시 사용
  static Future<dynamic> _deleteApi(String endPoint) async {
    String apiUrl = '$baseUrl/$endPoint';
    try {
      final response = await http.delete(Uri.parse(apiUrl));

      if (response.statusCode == 200) {
        debugPrint('Delete 요청 성공: $endPoint');
        return jsonDecode(response.body);
      } else {
        debugPrint(
            'Delete 요청 실패: $endPoint (${response.statusCode})${response.body}');
        return;
      }
    } catch (e) {
      debugPrint('Delete 요청 중 예외 발생: $e');
      return;
    }
  }

  /// 육류 이력관리 정보 (GET)
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
