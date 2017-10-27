export default ($resource) => {
  const ClauseService = $resource(
    '/api/clauses/:id',
    {},
    { update: { method: 'PUT' } });

  ClauseService.cache = { clause: undefined, original: undefined, annotationIndex: undefined };

  const oldGet = ClauseService.get;
  ClauseService.get = (params, cb, cb2) => {
    ClauseService.cache.clause = undefined;
    ClauseService.cache.original = undefined;
    ClauseService.cache.annotationIndex = undefined;
    return oldGet(params, (clause) => {
      ClauseService.cache.original = clause;
      ClauseService.reset();
      if (cb) {
        cb(clause);
      }
    }, (args) => { if (cb2) { cb2(args); } });
  };

  ClauseService.newAnnotation = () => ({
    annotation_idx: 0,
    invalid: 'uncertain',
    stative: 'uncertain',
    bounded: 'uncertain',
    extended: 'uncertain',
    change: 'uncertain',
    notes: '',
  });

  ClauseService.disable = () => {
    ClauseService.cache.clause = undefined;
    ClauseService.cache.original = undefined;
  };

  ClauseService.reset = () => {
    ClauseService.cache.clause = angular.copy(ClauseService.cache.original);
    if (!ClauseService.cache.clause.annotations.length) {
      ClauseService.cache.clause.annotations = [ClauseService.newAnnotation()];
    }
    if (ClauseService.cache.annotationIndex === undefined ||
        ClauseService.cache.annotationIndex < 0 ||
        ClauseService.cache.annotationIndex >= ClauseService.cache.clause.annotations.length) {
      ClauseService.cache.annotationIndex = 0;
    }
  };

  ClauseService.save = (resetAfter, success, error) => {
    if (ClauseService.cache.original) {
      const original = ClauseService.cache.original;
      angular.extend(original, ClauseService.cache.clause);
      const currentAnnotation = original.annotations[ClauseService.cache.annotationIndex];
      ClauseService.disable();
      return ClauseService.update(
        { id: original.id },
        currentAnnotation,
        (response) => {
          if (resetAfter) {
            ClauseService.cache.original = response;
            ClauseService.reset();
          }
          if (success) {
            success(response);
          }
        },
        error);
    }
  };

  ClauseService.isClean = () => (
    ClauseService.cache.original && angular.equals(
      ClauseService.cache.original,
      ClauseService.cache.clause)
  );

  return ClauseService;
};
