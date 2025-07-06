<template>
  <div class="landing-page">
    <!-- Top Notification Bar -->
    <div
      class="text-center py-2"
      style="background: linear-gradient(to right, #337665, #7baa73, #fac126); font-weight:500; margin-left: -10rem;"
    >
      Ready to ace your exams? Dive into <strong>Quizzy</strong> – your ultimate quiz companion!
      <router-link to="/register" class="text-decoration-underline text-dark ms-2">
        Start Your Journey Now →
      </router-link>
    </div>

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark"
    style="background: linear-gradient(90deg, #000, #7baa73); margin-left:-10rem; padding:0rem;">
      <div class="container-fluid">
        <a class="navbar-brand" style="font-size: 2rem; font-weight:500; font-family: serif" href="#">Quizzy</a>
        <div class="ms-auto">
          <router-link class="btn btn-outline-light me-2" to="/login">Log In</router-link>
          <router-link class="btn btn-light" to="/register">Sign Up</router-link>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section
      class="hero d-flex justify-content-center align-items-center text-white"
      style="min-height:85vh; min-width: 100vw;margin-left:-10rem; background: radial-gradient(circle at bottom, #123524, #123524, #337665, #7baa73, #fac126);">
      <div class="container-fluid px-4">
        <div class="row justify-content-center">
          <div class="col-12 col-md-8 text-center">
            <div class="mb-3">
              <span class="badge bg-transparent border border-light py-2 px-3"
                    style="font-size: 1rem; ">
                Quizzes That Actually Prep You
              </span>
            </div>
            <h1 class="display-3" style="font-family: serif;font-size: 6rem; font-weight:1000;">Learn Smarter<br/>Achieve More</h1>
            <p class="lead mb-4">
              Master chapters, ace quizzes, and stay ahead with personalized prep strategies..<br/>
              Whether you're a focused learner or a last-minute crammer, we’ve got you covered.
            </p>
            <router-link class="btn btn-light btn-lg" to="/register">Get Started</router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: "Landing",
};
</script>

<!-- <style scoped>
Optional: fade in animation
.hero {
  animation: fadeIn 1s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px) }
  to   { opacity: 1; transform: translateY(0) }
}
</style> -->
