export default ($resource) => {

  const ClauseService = $resource(
    '/api/clauses/:id',
    {},
    { update: { method: 'PUT' } });

  ClauseService.cache = { clause: undefined, original: undefined };

  const oldGet = ClauseService.get;
  ClauseService.get = (params, cb, cb2) => {
    ClauseService.cache.clause = undefined;
    ClauseService.cache.original = undefined;
    return oldGet(params, (clause) => {
      ClauseService.cache.original = clause;
      ClauseService.cache.clause = angular.copy(clause);
      if (cb) {
        cb(clause);
      }
    }, (args) => { if (cb2) { cb2(args); } });
  };

  ClauseService.save = (cb) => {
    if (ClauseService.cache.original) {
      angular.extend(ClauseService.cache.original, ClauseService.cache.clause);
      ClauseService.cache.original.$update((response) => {
        ClauseService.cache.original = response;
        ClauseService.cache.clause = angular.copy(response);
        if (cb) {
          cb(response);
        }
      });
    }
  };

  ClauseService.isClean = () => {
    return ClauseService.cache.original && angular.equals(ClauseService.cache.original,
                                                          ClauseService.cache.clause);
  };

  ClauseService.prototype.$update = function (cb) {  // eslint-disable-line
    return ClauseService.update({ id: this.id }, this.annotation, cb);  // eslint-disable-line
  };

  return ClauseService;

}
