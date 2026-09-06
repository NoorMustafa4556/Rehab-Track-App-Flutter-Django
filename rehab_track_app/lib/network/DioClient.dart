import 'package:dio/dio.dart';
import 'ApiEndpoints.dart';
import '../core/StorageService.dart';

class DioClient {
  static final Dio _dio = Dio(BaseOptions(
    baseUrl: ApiEndpoints.baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
    headers: {'Content-Type': 'application/json'},
  ));

  static Dio get instance {
    _dio.interceptors.clear();
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Attach token to every request
          final token = await StorageService.getAccessToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (DioException e, handler) async {
          // If 401 Unauthorized, try to refresh token
          if (e.response?.statusCode == 401) {
            final refreshToken = await StorageService.getRefreshToken();
            if (refreshToken != null) {
              try {
                // Call refresh endpoint
                final refreshResponse = await _dio.post(
                  ApiEndpoints.refresh,
                  data: {'refresh': refreshToken},
                );
                
                if (refreshResponse.statusCode == 200) {
                  final newAccessToken = refreshResponse.data['access'];
                  // If backend returns a new refresh token, use it; otherwise keep the old one
                  final newRefreshToken = refreshResponse.data['refresh'] ?? refreshToken;
                  
                  await StorageService.saveTokens(
                    access: newAccessToken,
                    refresh: newRefreshToken,
                  );

                  // Retry the failed request with new token
                  e.requestOptions.headers['Authorization'] = 'Bearer $newAccessToken';
                  final cloneReq = await _dio.request(
                    e.requestOptions.path,
                    options: Options(
                      method: e.requestOptions.method,
                      headers: e.requestOptions.headers,
                    ),
                    data: e.requestOptions.data,
                    queryParameters: e.requestOptions.queryParameters,
                  );
                  return handler.resolve(cloneReq);
                }
              } catch (refreshError) {
                // Refresh failed (e.g. refresh token expired), clear tokens
                await StorageService.clearTokens();
                // Should navigate to LoginScreen, but context is tricky here. 
                // We let the ViewModel handle the unauthenticated state.
              }
            } else {
              // No refresh token available
              await StorageService.clearTokens();
            }
          }
          return handler.next(e);
        },
      ),
    );
    return _dio;
  }
}
