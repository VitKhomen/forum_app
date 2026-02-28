<template>
  <!-- Завантаження -->
  <div v-if="loading" class="flex justify-center items-center py-32">
    <div class="flex flex-col items-center gap-4">
      <div class="animate-spin rounded-full h-14 w-14 border-4 border-gray-200 dark:border-gray-700 border-t-amber-400"></div>
      <p class="text-sm text-gray-400">Завантаження...</p>
    </div>
  </div>

  <!-- Не знайдено -->
  <div v-else-if="!movie" class="text-center py-32">
    <p class="text-6xl mb-4">🎬</p>
    <p class="text-xl font-semibold text-gray-700 dark:text-gray-300">Фільм не знайдено</p>
    <RouterLink to="/movies" class="mt-6 inline-flex items-center gap-2 px-5 py-2.5 bg-amber-400 text-gray-900 rounded-xl font-semibold hover:bg-amber-300 transition-colors">
      ← До кінотеки
    </RouterLink>
  </div>

  <!-- Основний контент -->
  <div v-else class="-mx-4 sm:-mx-6 lg:-mx-8 -mt-6">

    <!-- ══════════════════════════════════════
         HERO з backdrop
    ══════════════════════════════════════ -->
    <div class="relative overflow-hidden min-h-[520px] md:min-h-[580px]">
      <!-- Backdrop -->
      <Transition name="bg-fade" mode="out-in">
        <div
          :key="movie.id"
          class="absolute inset-0 bg-cover bg-top"
          :style="backdropUrl ? { backgroundImage: `url(${backdropUrl})` } : {}"
        />
      </Transition>
      <div v-if="!backdropUrl" class="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900" />

      <!-- Градієнти -->
      <div class="absolute inset-0 bg-gradient-to-r from-gray-950/98 via-gray-950/75 to-gray-950/30" />
      <div class="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/20 to-transparent" />

      <!-- Контент -->
      <div class="relative z-10 px-4 sm:px-6 lg:px-8 pt-10 pb-16 flex flex-col md:flex-row gap-8 md:gap-10 items-end">

        <!-- Постер -->
        <div class="flex-shrink-0 md:self-end">
          <div class="relative">
            <img
              v-if="posterUrl"
              :src="posterUrl"
              :alt="title"
              class="w-44 md:w-56 rounded-2xl shadow-2xl ring-1 ring-white/10"
            />
            <div v-else class="w-44 md:w-56 aspect-[2/3] rounded-2xl bg-gray-800 flex items-center justify-center ring-1 ring-white/10">
              <span class="text-6xl">🎬</span>
            </div>
            <!-- Рейтинговий бейдж -->
            <div v-if="movie.vote_average && movie.vote_average > 0" class="absolute -bottom-3 -right-3 w-14 h-14 rounded-full bg-amber-400 flex flex-col items-center justify-center shadow-xl ring-4 ring-gray-950">
              <span class="text-gray-900 font-black text-lg leading-none">{{ movie.vote_average.toFixed(1) }}</span>
              <span class="text-gray-700 text-[9px] leading-none font-medium">TMDB</span>
            </div>
          </div>
        </div>

        <!-- Метадані -->
        <div class="flex-1 text-white pb-2">
          <!-- Жанри -->
          <div class="flex flex-wrap gap-2 mb-4">
            <span
              v-for="genre in movie.genres"
              :key="genre.id"
              class="text-xs px-3 py-1 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-white/80"
            >{{ genre.name }}</span>
          </div>

          <!-- Назва -->
          <h1 class="text-3xl md:text-5xl font-black leading-tight mb-1 drop-shadow-xl">{{ title }}</h1>
          <p v-if="movie.original_title && movie.original_title !== title" class="text-white/40 text-sm italic mb-4">
            {{ movie.original_title }}
          </p>

          <!-- Рядок метадати -->
          <div class="flex flex-wrap items-center gap-3 text-sm text-white/60 mb-5">
            <span v-if="releaseYear">📅 {{ releaseYear }}</span>
            <span v-if="movie.runtime">⏱ {{ formatRuntime(movie.runtime) }}</span>
            <span v-if="movie.vote_count">💬 {{ movie.vote_count.toLocaleString() }} оцінок</span>
            <span v-if="movie.production_countries?.length">🌍 {{ movie.production_countries.map(c => c.iso_3166_1).join(', ') }}</span>
            <span
              v-if="movie.status"
              class="px-2 py-0.5 rounded-full text-xs font-medium"
              :class="movie.status === 'Released' ? 'bg-green-500/20 text-green-300 border border-green-500/30' : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'"
            >{{ statusLabel }}</span>
          </div>

          <!-- Tagline -->
          <p v-if="movie.tagline" class="text-white/50 italic text-base mb-3 border-l-2 border-amber-400/60 pl-3">
            "{{ movie.tagline }}"
          </p>

          <!-- Опис -->
          <p class="text-white/75 text-sm leading-relaxed line-clamp-3 max-w-2xl mb-6">{{ movie.overview }}</p>

          <!-- Кнопки -->
          <div class="flex flex-wrap gap-3">
            <button
              @click="toggleWatchlist"
              :disabled="actionLoading.watchlist"
              class="flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition-all disabled:opacity-60"
              :class="userState.in_watchlist
                ? 'bg-blue-500 text-white hover:bg-blue-600 shadow-lg shadow-blue-500/30'
                : 'bg-white/10 text-white hover:bg-white/20 backdrop-blur-sm border border-white/20'"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z"/></svg>
              {{ userState.in_watchlist ? 'У вотчлисті ✓' : 'Хочу дивитись' }}
            </button>

            <button
              @click="toggleFavorite"
              :disabled="actionLoading.favorite"
              class="flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition-all disabled:opacity-60"
              :class="userState.is_favorite
                ? 'bg-red-500 text-white hover:bg-red-600 shadow-lg shadow-red-500/30'
                : 'bg-white/10 text-white hover:bg-white/20 backdrop-blur-sm border border-white/20'"
            >
              {{ userState.is_favorite ? '❤️ Улюблений' : '🤍 В улюблені' }}
            </button>

            <button
              v-if="trailer"
              @click="scrollTo('trailer-section')"
              class="flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm bg-amber-400 hover:bg-amber-300 text-gray-900 transition-all shadow-lg shadow-amber-400/30"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/></svg>
              Трейлер
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════
         ОСНОВНИЙ КОНТЕНТ
    ══════════════════════════════════════ -->
    <div class="px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

        <!-- ЛІВА КОЛОНКА -->
        <div class="lg:col-span-2 space-y-6">

          <!-- Повний опис -->
          <section class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              📖 Про фільм
            </h2>
            <p class="text-gray-700 dark:text-gray-300 leading-relaxed">{{ movie.overview || 'Опис відсутній.' }}</p>
          </section>

          <!-- ══ ТРЕЙЛЕР великий ══ -->
          <section v-if="trailer" id="trailer-section" class="rounded-2xl overflow-hidden shadow-2xl bg-black">
            <div class="px-5 py-3.5 bg-gray-950 border-b border-white/10 flex items-center justify-between">
              <h2 class="text-sm font-bold text-white flex items-center gap-2">
                🎬 Офіційний трейлер
                <span class="text-xs font-normal text-gray-500">— {{ trailer.name }}</span>
              </h2>
              <span class="text-xs text-gray-600">YouTube</span>
            </div>
            <div class="aspect-video">
              <iframe
                :src="`https://www.youtube.com/embed/${trailer.key}?rel=0&modestbranding=1`"
                class="w-full h-full"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
              />
            </div>
          </section>

          <!-- ══ ІНШІ ВІДЕО ══ -->
          <section v-if="otherVideos.length" class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">🎥 Відео ({{ otherVideos.length + 1 }})</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div
                v-for="video in otherVideos"
                :key="video.id"
                @click="openVideo(video)"
                class="group cursor-pointer"
              >
                <div class="relative aspect-video rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-800">
                  <img
                    :src="`https://img.youtube.com/vi/${video.key}/mqdefault.jpg`"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div class="absolute inset-0 bg-black/25 group-hover:bg-black/10 transition-all flex items-center justify-center">
                    <div class="w-11 h-11 rounded-full bg-white/90 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                      <svg class="w-5 h-5 text-gray-900 ml-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/>
                      </svg>
                    </div>
                  </div>
                  <div class="absolute top-2 left-2">
                    <span class="bg-black/60 text-white text-xs px-2 py-0.5 rounded-md backdrop-blur-sm">{{ video.type }}</span>
                  </div>
                </div>
                <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mt-2 line-clamp-1">{{ video.name }}</p>
              </div>
            </div>
          </section>

          <!-- ══ СКРІНШОТИ ══ -->
          <section v-if="screenshots.length" class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
              🖼 Кадри з фільму
              <span class="text-sm font-normal text-gray-400 ml-1">({{ screenshots.length }})</span>
            </h2>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div
                v-for="(img, i) in screenshots"
                :key="i"
                @click="openScreenshot(i)"
                class="aspect-video rounded-xl overflow-hidden cursor-pointer group relative"
              >
                <img
                  :src="`https://image.tmdb.org/t/p/w780${img.file_path}`"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  loading="lazy"
                />
                <div class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all flex items-center justify-center">
                  <div class="w-9 h-9 rounded-full bg-white/0 group-hover:bg-white/20 transition-all flex items-center justify-center">
                    <svg class="w-5 h-5 text-white opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- ══ АКТОРСЬКИЙ СКЛАД ══ -->
          <section v-if="cast.length" class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">🎭 У головних ролях</h2>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              <button v-for="actor in cast" :key="actor.id" @click="openPerson(actor.id)" class="flex items-center gap-3 group text-left hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl p-1.5 -m-1.5 transition-colors w-full">
                <div class="w-11 h-11 flex-shrink-0 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-800 ring-2 ring-gray-100 dark:ring-gray-700 group-hover:ring-amber-400/50 transition-all">
                  <img
                    v-if="actor.profile_path"
                    :src="`https://image.tmdb.org/t/p/w185${actor.profile_path}`"
                    :alt="actor.name"
                    class="w-full h-full object-cover"
                    loading="lazy"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center text-lg text-gray-400">👤</div>
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors line-clamp-1">{{ actor.name }}</p>
                  <p class="text-xs text-gray-400 line-clamp-1">{{ actor.character }}</p>
                </div>
              </button>
            </div>
          </section>

          <!-- ══ ЗНІМАЛЬНА КОМАНДА ══ -->
          <section v-if="crew.length" class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">🎬 Знімальна команда</h2>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <button v-for="person in crew" :key="person.credit_id" @click="openPerson(person.id)" class="flex items-center gap-3 group text-left hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl p-1.5 -m-1.5 transition-colors w-full">
                <div class="w-10 h-10 flex-shrink-0 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-800 group-hover:ring-2 group-hover:ring-amber-400/40 transition-all">
                  <img
                    v-if="person.profile_path"
                    :src="`https://image.tmdb.org/t/p/w185${person.profile_path}`"
                    class="w-full h-full object-cover"
                    loading="lazy"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center text-base text-gray-400">👤</div>
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors line-clamp-1">{{ person.name }}</p>
                  <p class="text-xs text-gray-400">{{ person.job }}</p>
                </div>
              </button>
            </div>
          </section>

          <!-- ══ СХОЖІ ФІЛЬМИ ══ -->
          <section v-if="similar.length" class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">🎞 Схожі фільми</h2>
            <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
              <RouterLink
                v-for="film in similar"
                :key="film.id"
                :to="mediaType === 'tv' ? `/tv/${film.id}` : `/movies/${film.id}`"
                class="group"
              >
                <div class="aspect-[2/3] rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-800 mb-1.5 shadow-sm group-hover:shadow-lg transition-all">
                  <img
                    v-if="film.poster_path"
                    :src="`https://image.tmdb.org/t/p/w185${film.poster_path}`"
                    :alt="film.title"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    loading="lazy"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center text-3xl text-gray-400">🎬</div>
                </div>
                <p class="text-xs font-medium text-gray-800 dark:text-gray-200 line-clamp-2 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors leading-snug">
                  {{ film.title }}
                </p>
                <p class="text-xs text-gray-400 mt-0.5">{{ film.release_date?.slice(0,4) }}</p>
              </RouterLink>
            </div>
          </section>

        </div>

        <!-- ПРАВА КОЛОНКА (сайдбар) -->
        <div class="space-y-5">

          <!-- Оцінка -->
          <div class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-5 shadow-sm">
            <h3 class="text-base font-bold text-gray-900 dark:text-white mb-4">⭐ Моя оцінка</h3>

            <div v-if="!isAuthenticated" class="text-center py-2">
              <p class="text-sm text-gray-400 mb-2">Увійдіть щоб оцінити</p>
              <RouterLink to="/login" class="text-sm text-amber-600 dark:text-amber-400 font-semibold hover:underline">Увійти →</RouterLink>
            </div>

            <div v-else>
              <div class="flex gap-0.5 mb-2 justify-center">
                <button
                  v-for="n in 10"
                  :key="n"
                  @click="setRating(n)"
                  @mouseenter="hoverRating = n"
                  @mouseleave="hoverRating = 0"
                  class="text-2xl transition-all hover:scale-125 focus:outline-none"
                  :class="n <= (hoverRating || userState.user_rating || 0) ? 'text-amber-400' : 'text-gray-200 dark:text-gray-700'"
                >★</button>
              </div>
              <p class="text-center text-sm text-gray-500 dark:text-gray-400 mb-3">
                <template v-if="userState.user_rating">
                  Ваша оцінка: <span class="font-bold text-amber-500">{{ userState.user_rating }}/10</span>
                </template>
                <template v-else>Клікніть зірку щоб оцінити</template>
              </p>
              <button
                v-if="userState.user_rating"
                @click="deleteRating"
                :disabled="actionLoading.rating"
                class="w-full text-xs text-red-400 hover:text-red-600 transition-colors py-1 disabled:opacity-50"
              >Видалити оцінку</button>
            </div>
          </div>

          <!-- Деталі -->
          <div class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-5 shadow-sm">
            <h3 class="text-base font-bold text-gray-900 dark:text-white mb-4">📋 Деталі</h3>
            <dl class="space-y-2.5">
              <div v-if="movie.release_date" class="flex justify-between gap-3 text-sm">
                <dt class="text-gray-400 flex-shrink-0">Дата виходу</dt>
                <dd class="text-gray-900 dark:text-white font-medium text-right">{{ formatDate(movie.release_date) }}</dd>
              </div>
              <div v-if="movie.runtime" class="flex justify-between gap-3 text-sm">
                <dt class="text-gray-400 flex-shrink-0">Тривалість</dt>
                <dd class="text-gray-900 dark:text-white font-medium">{{ formatRuntime(movie.runtime) }}</dd>
              </div>
              <div v-if="movie.budget" class="flex justify-between gap-3 text-sm">
                <dt class="text-gray-400 flex-shrink-0">Бюджет</dt>
                <dd class="text-gray-900 dark:text-white font-medium">${{ formatMoney(movie.budget) }}</dd>
              </div>
              <div v-if="movie.revenue" class="flex justify-between gap-3 text-sm">
                <dt class="text-gray-400 flex-shrink-0">Збори</dt>
                <dd class="text-green-600 dark:text-green-400 font-medium">${{ formatMoney(movie.revenue) }}</dd>
              </div>
              <div v-if="movie.production_countries?.length" class="flex justify-between gap-3 text-sm">
                <dt class="text-gray-400 flex-shrink-0">Країна</dt>
                <dd class="text-gray-900 dark:text-white font-medium text-right">{{ movie.production_countries.map(c => c.name).join(', ') }}</dd>
              </div>
              <div v-if="movie.spoken_languages?.length" class="flex justify-between gap-3 text-sm">
                <dt class="text-gray-400 flex-shrink-0">Мова</dt>
                <dd class="text-gray-900 dark:text-white font-medium text-right">{{ movie.spoken_languages.map(l => l.name).join(', ') }}</dd>
              </div>
              <div v-if="movie.original_language" class="flex justify-between gap-3 text-sm">
                <dt class="text-gray-400 flex-shrink-0">Оригінал</dt>
                <dd class="text-gray-900 dark:text-white font-medium uppercase">{{ movie.original_language }}</dd>
              </div>
            </dl>
          </div>

          <!-- Режисер -->
          <div v-if="director" class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-5 shadow-sm">
            <h3 class="text-base font-bold text-gray-900 dark:text-white mb-4">🎬 Режисер</h3>
            <button @click="openPerson(director.id)" class="flex items-center gap-3 w-full text-left group hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl p-2 -m-2 transition-colors">
              <div class="w-14 h-14 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-800 flex-shrink-0 ring-2 ring-amber-400/30 group-hover:ring-amber-400/70 transition-all">
                <img
                  v-if="director.profile_path"
                  :src="`https://image.tmdb.org/t/p/w185${director.profile_path}`"
                  :alt="director.name"
                  class="w-full h-full object-cover"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-2xl">🎬</div>
              </div>
              <div>
                <p class="font-semibold text-gray-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">{{ director.name }}</p>
                <p class="text-xs text-gray-400">Режисер ↗</p>
              </div>
            </button>
          </div>

          <!-- Студії -->
          <div v-if="movie.production_companies?.length" class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-5 shadow-sm">
            <h3 class="text-base font-bold text-gray-900 dark:text-white mb-4">🏢 Студії</h3>
            <div class="space-y-3">
              <div v-for="company in movie.production_companies.slice(0, 4)" :key="company.id" class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 flex items-center justify-center flex-shrink-0 p-1.5 overflow-hidden">
                  <img
                    v-if="company.logo_path"
                    :src="`https://image.tmdb.org/t/p/w92${company.logo_path}`"
                    class="max-w-full max-h-full object-contain"
                  />
                  <span v-else class="text-gray-400 text-xs font-bold">{{ company.name[0] }}</span>
                </div>
                <p class="text-sm text-gray-700 dark:text-gray-300 font-medium line-clamp-1">{{ company.name }}</p>
              </div>
            </div>
          </div>

          <!-- Колекція -->
          <RouterLink
            v-if="movie.belongs_to_collection"
            :to="`/movies?collection=${movie.belongs_to_collection.id}`"
            class="block bg-gradient-to-br from-violet-500/10 to-purple-600/10 border border-violet-200 dark:border-violet-800/50 rounded-2xl p-5 hover:from-violet-500/20 hover:to-purple-600/20 transition-all group shadow-sm"
          >
            <div class="flex items-center gap-3">
              <div class="w-12 h-16 rounded-lg overflow-hidden bg-gray-200 dark:bg-gray-700 flex-shrink-0">
                <img
                  v-if="movie.belongs_to_collection.poster_path"
                  :src="`https://image.tmdb.org/t/p/w92${movie.belongs_to_collection.poster_path}`"
                  class="w-full h-full object-cover"
                />
              </div>
              <div>
                <p class="text-xs text-violet-500 font-semibold uppercase tracking-wider mb-0.5">Частина серії</p>
                <p class="font-bold text-gray-900 dark:text-white group-hover:text-violet-600 dark:group-hover:text-violet-400 transition-colors leading-snug">
                  {{ movie.belongs_to_collection.name }}
                </p>
              </div>
            </div>
          </RouterLink>

        </div>
      </div>
    </div>

    <!-- ══ ЛАЙТБОКС скріншотів ══ -->
    <Teleport to="body">
      <Transition name="lb-fade">
        <div
          v-if="lightbox.open"
          class="fixed inset-0 z-50 bg-black/96 flex items-center justify-center p-4"
          @click.self="lightbox.open = false"
          tabindex="0"
          ref="lightboxEl"
          @keydown="handleLightboxKey"
        >
          <!-- Закрити -->
          <button @click="lightbox.open = false" class="absolute top-4 right-4 p-2 text-white/50 hover:text-white transition-colors z-10">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>

          <!-- Попередній -->
          <button @click="prevScreenshot" class="absolute left-3 md:left-6 p-3 text-white/50 hover:text-white transition-colors hover:bg-white/10 rounded-full">
            <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>

          <!-- Зображення -->
          <Transition name="img-swap" mode="out-in">
            <img
              :key="lightbox.index"
              :src="`https://image.tmdb.org/t/p/original${screenshots[lightbox.index]?.file_path}`"
              class="max-w-full rounded-xl object-contain shadow-2xl"
              style="max-height: 88vh;"
            />
          </Transition>

          <!-- Наступний -->
          <button @click="nextScreenshot" class="absolute right-3 md:right-6 p-3 text-white/50 hover:text-white transition-colors hover:bg-white/10 rounded-full">
            <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </button>

          <!-- Лічильник -->
          <div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2">
            <span class="text-white/40 text-sm">{{ lightbox.index + 1 }} / {{ screenshots.length }}</span>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ══ Відео плеєр ══ -->
    <Teleport to="body">
      <Transition name="lb-fade">
        <div
          v-if="activeVideo"
          class="fixed inset-0 z-50 bg-black/96 flex items-center justify-center p-4"
          @click.self="activeVideo = null"
        >
          <button @click="activeVideo = null" class="absolute top-4 right-4 p-2 text-white/50 hover:text-white transition-colors">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
          <div class="w-full max-w-5xl aspect-video">
            <iframe
              :src="`https://www.youtube.com/embed/${activeVideo.key}?autoplay=1&rel=0&modestbranding=1`"
              class="w-full h-full rounded-2xl"
              frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            />
          </div>
        </div>
      </Transition>
    </Teleport>

  <!-- PersonModal -->
  <PersonModal v-model="showPersonModal" :person-id="selectedPersonId" />

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { moviesAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import PersonModal from '@/components/movies/PersonModal.vue'

// Props від роутера — mediaType передається для /tv/:id
const props = defineProps({
  mediaType: { type: String, default: 'movie' }
})

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const toast = useToast()

const route = useRoute()
// ID фільму/серіалу з URL, тип медіа з props (router передає 'tv' для /tv/:id)
const movieId = computed(() => route.params.id)
const mediaType = computed(() => props.mediaType || 'movie')

const movie       = ref(null)
const loading     = ref(true)
const hoverRating = ref(0)
const activeVideo = ref(null)
const lightboxEl  = ref(null)
const lightbox    = ref({ open: false, index: 0 })
const showPersonModal  = ref(false)
const selectedPersonId = ref(null)
const openPerson = (id) => { selectedPersonId.value = id; showPersonModal.value = true }

const userState = ref({ in_watchlist: false, is_favorite: false, user_rating: null })
const actionLoading = ref({ watchlist: false, favorite: false, rating: false })

// ─── Computed ──────────────────────────────────────────────────
const title       = computed(() => movie.value?.title || movie.value?.name || '')
const releaseYear = computed(() => (movie.value?.release_date || movie.value?.first_air_date)?.slice(0, 4))
const posterUrl   = computed(() => movie.value?.poster_path ? `https://image.tmdb.org/t/p/w500${movie.value.poster_path}` : null)
const backdropUrl = computed(() => movie.value?.backdrop_path ? `https://image.tmdb.org/t/p/w1280${movie.value.backdrop_path}` : null)

const allVideos   = computed(() => (movie.value?.videos?.results || []).filter(v => v.site === 'YouTube'))
const trailer     = computed(() => allVideos.value.find(v => v.type === 'Trailer') || allVideos.value.find(v => v.type === 'Teaser') || null)
const otherVideos = computed(() => allVideos.value.filter(v => v.id !== trailer.value?.id).slice(0, 6))

// Скріншоти — backdrops без мовних водяних знаків (iso_639_1 === null)
const screenshots = computed(() =>
  (movie.value?.images?.backdrops || [])
    .filter(img => !img.iso_639_1)
    .slice(0, 15)
)

const cast = computed(() => (movie.value?.credits?.cast || []).slice(0, 12))

const crew = computed(() => {
  const important = ['Director', 'Producer', 'Screenplay', 'Writer', 'Director of Photography', 'Original Music Composer']
  const seen = new Set()
  return (movie.value?.credits?.crew || [])
    .filter(p => {
      if (!important.includes(p.job) || seen.has(p.name)) return false
      seen.add(p.name)
      return true
    })
    .slice(0, 8)
})

const director    = computed(() => (movie.value?.credits?.crew || []).find(p => p.job === 'Director') || null)
const similar     = computed(() => (movie.value?.similar?.results || []).slice(0, 12))
const statusLabel = computed(() => {
  const map = { Released: 'Вийшов', 'In Production': 'У виробництві', 'Post Production': 'Пост-продакшн', 'Planned': 'Анонсовано' }
  return map[movie.value?.status] || movie.value?.status
})

// ─── Методи ────────────────────────────────────────────────────
const scrollTo = (id) => {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const openScreenshot = async (i) => {
  lightbox.value = { open: true, index: i }
  await nextTick()
  lightboxEl.value?.focus()
}
const prevScreenshot = () => { lightbox.value.index = (lightbox.value.index - 1 + screenshots.value.length) % screenshots.value.length }
const nextScreenshot = () => { lightbox.value.index = (lightbox.value.index + 1) % screenshots.value.length }
const handleLightboxKey = (e) => {
  if (e.key === 'ArrowLeft')  prevScreenshot()
  if (e.key === 'ArrowRight') nextScreenshot()
  if (e.key === 'Escape')     lightbox.value.open = false
}

const openVideo = (video) => { activeVideo.value = video }

// ─── Дії ──────────────────────────────────────────────────────
const toggleWatchlist = async () => {
  if (!isAuthenticated.value) { toast.warning('Увійдіть щоб додати до списку'); return }
  actionLoading.value.watchlist = true
  try {
    if (userState.value.in_watchlist) {
      await moviesAPI.removeWatchlist(movieId.value)
      userState.value.in_watchlist = false
      toast.success('Видалено зі списку')
    } else {
      await moviesAPI.toggleWatchlist(movieId.value)
      userState.value.in_watchlist = true
      toast.success('Додано до вотчлиста ✓')
    }
  } catch { toast.error('Помилка') } finally { actionLoading.value.watchlist = false }
}

const toggleFavorite = async () => {
  if (!isAuthenticated.value) { toast.warning('Увійдіть щоб додати до улюблених'); return }
  actionLoading.value.favorite = true
  try {
    if (userState.value.is_favorite) {
      await moviesAPI.removeFavorite(movieId.value)
      userState.value.is_favorite = false
      toast.success('Видалено з улюблених')
    } else {
      await moviesAPI.toggleFavorite(movieId.value)
      userState.value.is_favorite = true
      toast.success('Додано до улюблених ❤️')
    }
  } catch { toast.error('Помилка') } finally { actionLoading.value.favorite = false }
}

const setRating = async (rating) => {
  if (!isAuthenticated.value) return
  actionLoading.value.rating = true
  try {
    if (userState.value.user_rating) await moviesAPI.updateRating(movieId.value, rating)
    else await moviesAPI.rateMovie(movieId.value, rating)
    userState.value.user_rating = rating
    toast.success(`Оцінка ${rating}/10 збережена ⭐`)
  } catch { toast.error('Помилка збереження оцінки') } finally { actionLoading.value.rating = false }
}

const deleteRating = async () => {
  actionLoading.value.rating = true
  try {
    await moviesAPI.deleteRating(movieId.value)
    userState.value.user_rating = null
    toast.success('Оцінку видалено')
  } catch { toast.error('Помилка') } finally { actionLoading.value.rating = false }
}

// ─── Форматування ─────────────────────────────────────────────
const formatRuntime = (m) => { const h = Math.floor(m / 60), min = m % 60; return h ? `${h}г ${min}хв` : `${min}хв` }
const formatDate = (s) => s ? new Date(s).toLocaleDateString('uk-UA', { day: 'numeric', month: 'long', year: 'numeric' }) : ''
const formatMoney = (n) => {
  if (!n) return '—'
  if (n >= 1e9) return (n / 1e9).toFixed(1) + 'B'
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M'
  return n.toLocaleString()
}

// ─── Fetch ────────────────────────────────────────────────────
const fetchMovie = async () => {
  loading.value = true
  window.scrollTo({ top: 0 })
  try {
    const { data } = await moviesAPI.getById(movieId.value, mediaType.value)
    movie.value = data
    userState.value = {
      in_watchlist: data.user_state?.in_watchlist || false,
      is_favorite:  data.user_state?.is_favorite  || false,
      user_rating:  data.user_state?.user_rating   || null,
    }
  } catch { movie.value = null }
  finally { loading.value = false }
}

watch([() => route.params.id, () => props.mediaType], fetchMovie)
onMounted(fetchMovie)
</script>

<style scoped>
.bg-fade-enter-active, .bg-fade-leave-active { transition: opacity 1s ease; }
.bg-fade-enter-from, .bg-fade-leave-to { opacity: 0; }

.lb-fade-enter-active, .lb-fade-leave-active { transition: opacity 0.2s ease; }
.lb-fade-enter-from, .lb-fade-leave-to { opacity: 0; }

.img-swap-enter-active, .img-swap-leave-active { transition: opacity 0.15s ease; }
.img-swap-enter-from, .img-swap-leave-to { opacity: 0; }
</style>