import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:mobile/l10n/app_localizations.dart';
import 'package:mobile/l10n/current_localizations.dart';

import '../data/supabase_tables.dart';
import 'person_profile.dart';

String _peopleL10n(String Function(AppLocalizations l10n) selector) =>
    selector(currentL10n());

class PeopleQueryException implements Exception {
  const PeopleQueryException({
    required this.operation,
    required this.table,
    required this.endpoint,
    required this.message,
    this.cause,
  });

  final String operation;
  final String table;
  final String endpoint;
  final String message;
  final Object? cause;

  String get userMessage =>
      '$message (table: $table, op: $operation, endpoint: $endpoint)';

  @override
  String toString() => userMessage;
}

class PeopleRepository {
  PeopleRepository({SupabaseClient? client})
    : _client = client ?? Supabase.instance.client;

  final SupabaseClient _client;
  String? _resolvedTable;

  static const String _peopleSelect =
      'id,owner_user_id,name,birth_date,birth_time,city,country,timezone,created_at';

  Future<List<PersonProfile>> listPeople(String ownerUserId) async {
    final table = await _resolvePeopleTable(operation: 'listPeople');
    if (table == SupabaseTables.profiles) {
      return _listPeopleFromProfiles(table: table, ownerUserId: ownerUserId);
    }

    final endpoint =
        '/$table?select=$_peopleSelect&owner_user_id=eq.$ownerUserId';
    try {
      final rows = await _client
          .from(table)
          .select(_peopleSelect)
          .eq('owner_user_id', ownerUserId)
          .order('created_at', ascending: false);

      return _toPersonList(rows);
    } catch (error) {
      _logFailure(
        operation: 'listPeople',
        table: table,
        endpoint: endpoint,
        error: error,
      );
      throw PeopleQueryException(
        operation: 'listPeople',
        table: table,
        endpoint: endpoint,
        message: _peopleL10n((l10n) => l10n.peopleRepoListFailed),
        cause: error,
      );
    }
  }

  Future<PersonProfile?> getPerson({
    required String ownerUserId,
    required String personId,
  }) async {
    final table = await _resolvePeopleTable(operation: 'getPerson');
    if (table == SupabaseTables.profiles) {
      return _getPersonFromProfiles(
        table: table,
        ownerUserId: ownerUserId,
        personId: personId,
      );
    }

    final endpoint = '/$table?select=$_peopleSelect&id=eq.$personId';
    try {
      final row = await _client
          .from(table)
          .select(_peopleSelect)
          .eq('owner_user_id', ownerUserId)
          .eq('id', personId)
          .limit(1)
          .maybeSingle();

      if (row == null) {
        return null;
      }
      return PersonProfile.fromMap(Map<String, dynamic>.from(row));
    } catch (error) {
      _logFailure(
        operation: 'getPerson',
        table: table,
        endpoint: endpoint,
        error: error,
      );
      throw PeopleQueryException(
        operation: 'getPerson',
        table: table,
        endpoint: endpoint,
        message: _peopleL10n((l10n) => l10n.peopleRepoDetailFailed),
        cause: error,
      );
    }
  }

  Future<PersonProfile> createPerson({
    required String ownerUserId,
    required String name,
    required String birthDate,
    String? birthTime,
    required String city,
    required String country,
    String timezone = 'Europe/Istanbul',
  }) async {
    final table = await _resolvePeopleTable(operation: 'createPerson');
    final cleanBirthTime = (birthTime ?? '').trim().isEmpty ? null : birthTime;

    if (table == SupabaseTables.profiles) {
      return _createPersonInProfiles(
        table: table,
        ownerUserId: ownerUserId,
        name: name,
        birthDate: birthDate,
        birthTime: cleanBirthTime,
        city: city,
        country: country,
        timezone: timezone,
      );
    }

    final payload = <String, dynamic>{
      'owner_user_id': ownerUserId,
      'name': name,
      'birth_date': birthDate,
      'birth_time': cleanBirthTime,
      'city': city,
      'country': country,
      'timezone': timezone,
    };

    final endpoint = '/$table?insert';
    try {
      final row = await _client
          .from(table)
          .insert(payload)
          .select(_peopleSelect)
          .single();

      return PersonProfile.fromMap(Map<String, dynamic>.from(row));
    } catch (error) {
      _logFailure(
        operation: 'createPerson',
        table: table,
        endpoint: endpoint,
        error: error,
      );
      throw PeopleQueryException(
        operation: 'createPerson',
        table: table,
        endpoint: endpoint,
        message: _peopleL10n((l10n) => l10n.peopleRepoCreateFailed),
        cause: error,
      );
    }
  }

  Future<PersonProfile> updatePerson({
    required String ownerUserId,
    required String personId,
    required String name,
    required String birthDate,
    String? birthTime,
    required String city,
    required String country,
    String timezone = 'Europe/Istanbul',
  }) async {
    final table = await _resolvePeopleTable(operation: 'updatePerson');
    final cleanBirthTime = (birthTime ?? '').trim().isEmpty ? null : birthTime;

    if (table == SupabaseTables.profiles) {
      return _updatePersonInProfiles(
        table: table,
        ownerUserId: ownerUserId,
        personId: personId,
        name: name,
        birthDate: birthDate,
        birthTime: cleanBirthTime,
        city: city,
        country: country,
        timezone: timezone,
      );
    }

    final payload = <String, dynamic>{
      'name': name,
      'birth_date': birthDate,
      'birth_time': cleanBirthTime,
      'city': city,
      'country': country,
      'timezone': timezone,
    };

    final endpoint = '/$table?id=eq.$personId&owner_user_id=eq.$ownerUserId';
    try {
      final row = await _client
          .from(table)
          .update(payload)
          .eq('owner_user_id', ownerUserId)
          .eq('id', personId)
          .select(_peopleSelect)
          .single();

      return PersonProfile.fromMap(Map<String, dynamic>.from(row));
    } catch (error) {
      _logFailure(
        operation: 'updatePerson',
        table: table,
        endpoint: endpoint,
        error: error,
      );
      throw PeopleQueryException(
        operation: 'updatePerson',
        table: table,
        endpoint: endpoint,
        message: _peopleL10n((l10n) => l10n.peopleRepoUpdateFailed),
        cause: error,
      );
    }
  }

  Future<List<PersonProfile>> _listPeopleFromProfiles({
    required String table,
    required String ownerUserId,
  }) async {
    const select =
        'id,owner_user_id,name,full_name,birth_date,birth_time,city,country,timezone,created_at';
    final endpoint = '/$table?select=$select&owner_user_id=eq.$ownerUserId';
    try {
      final rows = await _client
          .from(table)
          .select(select)
          .eq('owner_user_id', ownerUserId)
          .order('created_at', ascending: false);
      return _toPersonList(rows);
    } catch (error) {
      _logFailure(
        operation: 'listPeople',
        table: table,
        endpoint: endpoint,
        error: error,
      );
      throw PeopleQueryException(
        operation: 'listPeople',
        table: table,
        endpoint: endpoint,
        message: _peopleL10n((l10n) => l10n.peopleRepoProfilesListUnsupported),
        cause: error,
      );
    }
  }

  Future<PersonProfile?> _getPersonFromProfiles({
    required String table,
    required String ownerUserId,
    required String personId,
  }) async {
    const select =
        'id,owner_user_id,name,full_name,birth_date,birth_time,city,country,timezone,created_at';
    final endpoint = '/$table?select=$select&id=eq.$personId';
    try {
      final row = await _client
          .from(table)
          .select(select)
          .eq('owner_user_id', ownerUserId)
          .eq('id', personId)
          .limit(1)
          .maybeSingle();
      if (row == null) {
        return null;
      }
      return PersonProfile.fromMap(Map<String, dynamic>.from(row));
    } catch (error) {
      _logFailure(
        operation: 'getPerson',
        table: table,
        endpoint: endpoint,
        error: error,
      );
      throw PeopleQueryException(
        operation: 'getPerson',
        table: table,
        endpoint: endpoint,
        message: _peopleL10n(
          (l10n) => l10n.peopleRepoProfilesDetailUnsupported,
        ),
        cause: error,
      );
    }
  }

  Future<PersonProfile> _createPersonInProfiles({
    required String table,
    required String ownerUserId,
    required String name,
    required String birthDate,
    required String? birthTime,
    required String city,
    required String country,
    required String timezone,
  }) async {
    final endpoint = '/$table?insert';
    final payloadVariants = <Map<String, dynamic>>[
      <String, dynamic>{
        'owner_user_id': ownerUserId,
        'name': name,
        'birth_date': birthDate,
        'birth_time': birthTime,
        'city': city,
        'country': country,
        'timezone': timezone,
      },
      <String, dynamic>{
        'owner_user_id': ownerUserId,
        'full_name': name,
        'birth_date': birthDate,
        'birth_time': birthTime,
        'city': city,
        'country': country,
        'timezone': timezone,
      },
    ];

    Object? lastError;
    for (final payload in payloadVariants) {
      try {
        final row = await _client.from(table).insert(payload).select().single();
        return PersonProfile.fromMap(Map<String, dynamic>.from(row));
      } catch (error) {
        lastError = error;
      }
    }

    _logFailure(
      operation: 'createPerson',
      table: table,
      endpoint: endpoint,
      error: lastError ?? 'unknown',
    );
    throw PeopleQueryException(
      operation: 'createPerson',
      table: table,
      endpoint: endpoint,
      message: _peopleL10n((l10n) => l10n.peopleRepoProfilesCreateUnsupported),
      cause: lastError,
    );
  }

  Future<PersonProfile> _updatePersonInProfiles({
    required String table,
    required String ownerUserId,
    required String personId,
    required String name,
    required String birthDate,
    required String? birthTime,
    required String city,
    required String country,
    required String timezone,
  }) async {
    final endpoint = '/$table?id=eq.$personId&owner_user_id=eq.$ownerUserId';
    final payloadVariants = <Map<String, dynamic>>[
      <String, dynamic>{
        'name': name,
        'birth_date': birthDate,
        'birth_time': birthTime,
        'city': city,
        'country': country,
        'timezone': timezone,
      },
      <String, dynamic>{
        'full_name': name,
        'birth_date': birthDate,
        'birth_time': birthTime,
        'city': city,
        'country': country,
        'timezone': timezone,
      },
    ];

    Object? lastError;
    for (final payload in payloadVariants) {
      try {
        final row = await _client
            .from(table)
            .update(payload)
            .eq('owner_user_id', ownerUserId)
            .eq('id', personId)
            .select()
            .single();
        return PersonProfile.fromMap(Map<String, dynamic>.from(row));
      } catch (error) {
        lastError = error;
      }
    }

    _logFailure(
      operation: 'updatePerson',
      table: table,
      endpoint: endpoint,
      error: lastError ?? 'unknown',
    );
    throw PeopleQueryException(
      operation: 'updatePerson',
      table: table,
      endpoint: endpoint,
      message: _peopleL10n((l10n) => l10n.peopleRepoUpdateFailed),
      cause: lastError,
    );
  }

  List<PersonProfile> _toPersonList(dynamic rows) {
    final out = <PersonProfile>[];
    for (final row in rows as List<dynamic>) {
      if (row is Map) {
        out.add(PersonProfile.fromMap(Map<String, dynamic>.from(row)));
      }
    }
    return out;
  }

  Future<String> _resolvePeopleTable({required String operation}) async {
    final cached = _resolvedTable;
    if (cached != null) {
      return cached;
    }

    for (final table in SupabaseTables.peopleCandidates) {
      final schemaOk = await _probeTableSchema(table: table);
      if (schemaOk) {
        _resolvedTable = table;
        debugPrint(
          '[PeopleRepository] Resolved table for $operation => $table',
        );
        return table;
      }
    }

    const fallbackTable = SupabaseTables.peopleProfiles;
    throw PeopleQueryException(
      operation: operation,
      table: fallbackTable,
      endpoint: '/$fallbackTable?select=id',
      message: _peopleL10n(
        (l10n) => l10n.peopleRepoTableNotFound(
          SupabaseTables.peopleCandidates.join(', '),
        ),
      ),
    );
  }

  Future<bool> _probeTableSchema({required String table}) async {
    final String select;
    if (table == SupabaseTables.profiles) {
      select =
          'id,owner_user_id,name,full_name,birth_date,birth_time,city,country,timezone,created_at';
    } else {
      select = _peopleSelect;
    }

    try {
      await _client.from(table).select(select).limit(1);
      return true;
    } on PostgrestException catch (error) {
      if (_isMissingTable(error) || _isMissingColumn(error)) {
        debugPrint(
          '[PeopleRepository] Table probe skipped $table: ${error.code} ${error.message}',
        );
        return false;
      }
      _logFailure(
        operation: 'probeTable',
        table: table,
        endpoint: '/$table?select=$select&limit=1',
        error: error,
      );
      throw PeopleQueryException(
        operation: 'probeTable',
        table: table,
        endpoint: '/$table?select=$select&limit=1',
        message: _peopleL10n((l10n) => l10n.peopleRepoTableValidationFailed),
        cause: error,
      );
    }
  }

  bool _isMissingTable(PostgrestException error) {
    final message = error.message.toLowerCase();
    return error.code == 'PGRST205' ||
        error.code == 'PGREST205' ||
        (message.contains('could not find') && message.contains('table')) ||
        message.contains('schema cache');
  }

  bool _isMissingColumn(PostgrestException error) {
    return error.code == '42703' ||
        error.message.toLowerCase().contains('column') &&
            error.message.toLowerCase().contains('does not exist');
  }

  void _logFailure({
    required String operation,
    required String table,
    required String endpoint,
    required Object error,
  }) {
    debugPrint(
      '[PeopleRepository] operation=$operation table=$table endpoint=$endpoint error=$error',
    );
  }
}
