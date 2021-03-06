import template from './interface.html';
import SPAN_TITLES from './labels';

// https://stackoverflow.com/a/8069367/1062499
function range(low, high) {
  const list = [];
  for (let i = low; i < high; i += 1) {
    list.push(i);
  }
  return list;
}

function getSpanMaps(clause) {
  const spanMap = clause.sentence.map(() => undefined);
  const spanMap2 = clause.sentence.map(() => undefined);
  clause['aspectual-indicators'].forEach((comp) => {
    for (let i = comp.begin; i < comp.end; i += 1) {
      spanMap[i] = comp.type;
      spanMap2[i] = 'aspind';
    }
  });
  clause['verb-comps'].forEach((comp) => {
    for (let i = comp.begin; i < comp.end; i += 1) {
      spanMap[i] = comp.type;
      spanMap2[i] = 'synarg';
    }
  });
  spanMap[clause['verb-index']] = 'verb';
  spanMap2[clause['verb-index']] = undefined;
  if (clause['prefix-index']) {
    spanMap[clause['prefix-index']] = 'verb';
    spanMap2[clause['prefix-index']] = undefined;
  }
  return { spanMap, spanMap2 };
}

function getSpans(clause) {
  const spanMaps = getSpanMaps(clause);
  const spans = [];
  let lastClass;
  let currentSpan = { wclass: undefined, mclass: undefined, words: [] };
  for (let i = 0; i < clause.sentence.length; i += 1) {
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

function controller($scope, $rootScope, $routeParams, $location, $window, Clauses, $http) {
  $scope.spans = [];
  $scope.annotation = {};
  $scope.annotationButtons = [];
  $scope.currentAnnotation = '';

  const self = this;

  // we use the Clause service's cache to access the clause
  // object in the page
  $scope.cached = Clauses.cache;
  // keep track of whether we want to handle key events or not (we do
  // if the user is not currently in the "notes" text box, i.e., when
  // textFocus is false)
  $scope.textFocus = false;

  // make the call to the REST API to fetch the clause object
  Clauses.get(
    { id: $routeParams.clauseId },
    (clause) => {
      $scope.spans = getSpans(clause);
      this.initAnnotation();
    },
    () => { $location.url('/annotations/'); });

  this.initAnnotation = () => {
    // $scope holds a pointer to the current annotation object being
    // edited
    $scope.annotation = Clauses.cache.clause.annotations[Clauses.cache.annotationIndex];
    // set up an array to draw the buttons on the page which allow the
    // user to select which annotation they want to work on
    $scope.annotationButtons = range(0, Clauses.cache.clause.annotations.length).map(
      index => ({
        value: index.toString(), // '0'
        label: (index + 1).toString(), // '1'
        onChange: () => {
          if (Clauses.cache.annotationIndex !== index) {
            this.showAnnotation(index);
          }
        },
      }));
    // button to allow the user to create a new annotation
    $scope.annotationButtons.push({
      value: 'new',
      label: 'New annotation',
      onChange: () => { this.addAnnotation(); },
    });
    // create a value that will model the currently selected annotation
    $scope.currentAnnotation = Clauses.cache.annotationIndex.toString();
  };
  this.addAnnotation = () => {
    if (Clauses.cache.clause) {
      this.saveIfNeeded(true, () => {
        const newAnnotation = Clauses.newAnnotation();
        // set to 1 more than the biggest value found in Clauses.cache.clause
        newAnnotation.annotation_idx = Clauses.cache.clause.annotations
          .map(annotation => annotation.annotation_idx)
          .reduce((a, b) => Math.max(a, b), 0) + 1;
        Clauses.cache.clause.annotations.push(newAnnotation);
        Clauses.cache.annotationIndex = Clauses.cache.clause.annotations.length - 1;
        this.initAnnotation();
      });
    }
  };
  this.showAnnotation = (index) => {
    if (Clauses.cache.clause &&
        index >= 0 &&
        index < Clauses.cache.clause.annotations.length) {
      this.saveIfNeeded(true, () => {
        Clauses.cache.annotationIndex = index;
        this.initAnnotation();
      });
    }
  };
  $scope.reset = () => {
    Clauses.reset();
    this.initAnnotation();
  };
  $scope.invalidChanged = () => {
    if ($scope.annotation.invalid === 'true') {
      $scope.annotation.stative = 'uncertain';
      $scope.annotation.bounded = 'uncertain';
      $scope.annotation.extended = 'uncertain';
      $scope.annotation.change = 'uncertain';
    }
  };
  $scope.stativeChanged = () => {
    if ($scope.annotation.stative === 'false' || $scope.annotation.stative === 'true') {
      $scope.annotation.invalid = 'false';
    }
    if ($scope.annotation.stative === 'true') {
      $scope.annotation.bounded = 'false';
      $scope.annotation.extended = 'true';
      $scope.annotation.change = 'false';
    }
  };
  $scope.boundedChanged = () => {
    if ($scope.annotation.bounded === 'false' || $scope.annotation.bounded === 'true') {
      $scope.annotation.invalid = 'false';
      $scope.annotation.stative = 'false';
    }
    if ($scope.annotation.bounded === 'false') {
      $scope.annotation.extended = 'true';
      $scope.annotation.change = 'false';
    }
  };
  $scope.extendedChanged = () => {
    if ($scope.annotation.extended === 'false' || $scope.annotation.extended === 'true') {
      $scope.annotation.invalid = 'false';
      $scope.annotation.stative = 'false';
      $scope.annotation.bounded = 'true';
    }
  };
  $scope.changeChanged = () => {
    if ($scope.annotation.change === 'false' || $scope.annotation.change === 'true') {
      $scope.annotation.invalid = 'false';
      $scope.annotation.stative = 'false';
      $scope.annotation.bounded = 'true';
    }
  };
  $scope.shouldSave = () =>
    (Clauses.cache.original &&
     !Clauses.isClean() &&
     !($scope.annotation.invalid === 'uncertain' &&
       $scope.annotation.stative === 'uncertain' &&
       $scope.annotation.bounded === 'uncertain' &&
       $scope.annotation.extended === 'uncertain' &&
       $scope.annotation.change === 'uncertain' &&
       $scope.annotation.notes === ''));
  this.saveIfNeeded = (resetAfter, success, error) => {
    if ($scope.shouldSave()) {
      Clauses.save(resetAfter, () => {
        if (resetAfter) {
          this.initAnnotation();
        }
        success();
      }, error);
    } else {
      success();
    }
  };
  this.hasSearchResults = () =>
    self.searchResults !== undefined &&
    self.searchResults != null &&
    self.searchResults.length > 0;
  $scope.hasLeft = () => {
    if (!Clauses.cache.clause) return false;
    if (self.hasSearchResults()) {
      const result = self.searchResults.slice().reverse().find(i => i < Clauses.cache.clause.id);
      return result !== undefined && result !== -1;
    }
    return Clauses.cache.clause.id !== 1;
  };
  this.getLeft = () => {
    if (self.hasSearchResults()) {
      return self.searchResults.slice().reverse().find(i => i < Clauses.cache.clause.id);
    }
    return Clauses.cache.clause.id - 1;
  };
  $scope.left = () => {
    if ($scope.hasLeft()) {
      const newUrl = `/${self.getLeft()}`;
      self.saveIfNeeded(false, () => {
        $location.url(newUrl);
      });
    }
  };
  $scope.hasRight = () => {
    if (!Clauses.cache.clause) return false;
    if (self.hasSearchResults()) {
      const result = self.searchResults.find(i => i > Clauses.cache.clause.id);
      return result !== undefined && result !== -1;
    }
    return !Clauses.cache.clause.last;
  };
  this.getRight = () => {
    if (self.hasSearchResults()) {
      return self.searchResults.find(i => i > Clauses.cache.clause.id);
    }
    return Clauses.cache.clause.id + 1;
  };
  $scope.right = () => {
    if ($scope.hasRight()) {
      const newUrl = `/${self.getRight()}`;
      self.saveIfNeeded(false, () => {
        $location.url(newUrl);
      });
    }
  };
  $scope.clearSearch = () => {
    $scope.searchQuery = '';
    $scope.searchType = null;
    self.searchResults = [];
  };
  this.initSearch = () => {
    $scope.clearSearch();
    if ($window.localStorage) {
      try {
        $scope.searchQuery = JSON.parse($window.localStorage.getItem('searchQuery') || '""');
        $scope.searchType = JSON.parse($window.localStorage.getItem('searchType') || 'null');
        self.searchResults = JSON.parse($window.localStorage.getItem('searchResults') || '[]');
      } catch (e) {
        // do nothing
      }
    }
  };
  this.initSearch();
  this.persistSearch = () => {
    if ($window.localStorage) {
      try {
        $window.localStorage.setItem('searchQuery', JSON.stringify($scope.searchQuery));
        $window.localStorage.setItem('searchType', JSON.stringify($scope.searchType));
        $window.localStorage.setItem('searchResults', JSON.stringify(self.searchResults));
      } catch (e) {
        // do nothing
      }
    }
  };
  this.updateSearch = () => {
    const dropdownButton = angular.element(document.querySelector('#dropdown-button'));
    const caret = '<span class="caret">';
    if ($scope.searchType === 'verb') dropdownButton.html(`Verb&nbsp;${caret}`);
    else if ($scope.searchType === 'text') dropdownButton.html(`Text&nbsp;${caret}`);
    else dropdownButton.html(`Search By&nbsp;${caret}`);

    self.searchResults = [];
    if ($scope.searchQuery && $scope.searchType !== null) {
      $http.get(`/api/search/${$scope.searchType}/${$scope.searchQuery}`)
        .then(res => res.data)
        .then((matchingIds) => { self.searchResults = matchingIds; self.persistSearch(); })
        .catch(() => { self.persistSearch(); });
    } else {
      self.persistSearch();
    }
  };
  // use a watch method to update search
  $scope.$watch('searchQuery', (newValue, oldValue) => { if (newValue !== oldValue) { self.updateSearch(); } });
  $scope.$watch('searchType', (newValue, oldValue) => { if (newValue !== oldValue) { self.updateSearch(); } });
  this.keyDown = (event) => {
    // console.log('keyDown');
    // console.log(event); /* key event is here */
    if (Clauses.cache.clause && $scope.annotation &&
        !$scope.textFocus &&
        !event.altKey && !event.metaKey && !event.ctrlKey) {
      if (event.which === 37) {
        $scope.left(); // left
      }
      if (event.which === 39) {
        $scope.right(); // right
      }
      if (event.which === 27) {
        $scope.reset(); // ESCAPE
      }
      if (event.which === 73) {
        // i
        $scope.annotation.invalid = 'true';
        $scope.invalidChanged();
      }
      if (event.which === 86) {
        // v
        $scope.annotation.invalid = 'false';
        $scope.invalidChanged();
      }
      if (event.which === 83) {
        // s
        $scope.annotation.stative = 'true';
        $scope.stativeChanged();
      }
      if (event.which === 68) {
        // d
        $scope.annotation.stative = 'false';
        $scope.stativeChanged();
      }
      if (event.which === 85) {
        // u
        $scope.annotation.bounded = 'false';
        $scope.boundedChanged();
      }
      if (event.which === 66) {
        // b
        $scope.annotation.bounded = 'true';
        $scope.boundedChanged();
      }
      if (event.which === 69) {
        // e
        $scope.annotation.extended = 'true';
        $scope.extendedChanged();
      }
      if (event.which === 80) {
        // p
        $scope.annotation.extended = 'false';
        $scope.extendedChanged();
      }
      if (event.which === 67) {
        // c
        $scope.annotation.change = 'true';
        $scope.changeChanged();
      }
      if (event.which === 78) {
        // n
        $scope.annotation.change = 'false';
        $scope.changeChanged();
      }
    }
  };
  $rootScope.$on(
    'bodySendsKeyDown',
    (broadcastEvt, keyEvt) => {
      $rootScope.$evalAsync(() => { this.keyDown(keyEvt); });
    });
}

controller.$inject = ['$scope', '$rootScope', '$routeParams', '$location', '$window', 'Clauses', '$http'];

export default {
  restrict: 'E',
  controller,
  template,
};
