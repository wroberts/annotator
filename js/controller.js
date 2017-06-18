import template from './interface.html';

const SPAN_TITLES = {
  verb: 'Main verb of the clause',
  subj: 'Subject',
  obj: 'Direct object',
  advp_for: 'Aspectual (for)',
};

function getSpanMaps(clause) {
  const spanMap = clause.sentence.map(() => undefined);
  const spanMap2 = clause.sentence.map(() => undefined);
  for (const comp of clause['aspectual-indicators']) {
    for (let i = comp.begin; i < comp.end; i += 1) {
      spanMap[i] = comp.type;
      spanMap2[i] = 'aspind';
    }
  }
  for (const comp of clause['verb-comps']) {
    for (let i = comp.begin; i < comp.end; i += 1) {
      spanMap[i] = comp.type;
      spanMap2[i] = 'synarg';
    }
  }
  spanMap[clause['verb-index']] = 'verb';
  spanMap2[clause['verb-index']] = undefined;
  return { spanMap, spanMap2 };
}

function getSpans(clause) {
  const spanMaps = getSpanMaps(clause);
  const spans = [];
  let lastClass;
  let currentSpan = { wclass: undefined, mclass: undefined, words: [] };
  for (let i = 0; i < clause.sentence.length - 1; i += 1) {
    const word = clause.sentence[i];
    const wclass = spanMaps.spanMap[i];
    if (wclass === lastClass) {
      currentSpan.words.push(word);
    } else {
      lastClass = wclass;
      if (currentSpan.words) {
        currentSpan.idx = spans.length;
        currentSpan.title = SPAN_TITLES[currentSpan.wclass];
        if (currentSpan.title) currentSpan.cclass = 'help';
        currentSpan.words = currentSpan.words.join(' ');
        spans.push(currentSpan);
      }
      currentSpan = { wclass, mclass: spanMaps.spanMap2[i], words: [word] };
    }
  }
  if (currentSpan.words) {
    currentSpan.idx = spans.length;
    currentSpan.title = SPAN_TITLES[currentSpan.wclass];
    if (currentSpan.title) currentSpan.cclass = 'help';
    currentSpan.words = currentSpan.words.join(' ');
    spans.push(currentSpan);
  }
  return spans;
}

function controller($scope, $routeParams, Clauses) {
  // make the call to the REST API to fetch the clause object
  $scope.spans = [];
  $scope.annotation = {};
  Clauses.get({ id: $routeParams.clauseId },
              (clause) => {
                $scope.spans = getSpans(clause);
                if (!Clauses.cache.clause.annotation) {
                  Clauses.cache.clause.annotation = {
                    invalid: 'uncertain',
                    stative: 'uncertain',
                    bounded: 'uncertain',
                    change: 'uncertain'
                  };
                }
                $scope.annotation = Clauses.cache.clause.annotation;
              });
  // we use the Clause service's cache to access the clause
  // object in the page
  $scope.cached = Clauses.cache;
  $scope.isClean = Clauses.isClean;
  $scope.save = Clauses.save;
}

export default {
  restrict: 'E',
  controller,
  template,
};
