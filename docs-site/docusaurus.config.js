// @ts-check

const config = {
  title: 'Egeyuma Bhashanthara',
  tagline: 'Local-first Sinhala benchmark translation and verification',

  url: 'https://dishanrajapaksha.github.io',
  baseUrl: '/egeyuma-bhashanthara/',

  organizationName: 'DishanRajapaksha',
  projectName: 'egeyuma-bhashanthara',

  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          path: '../docs',
          routeBasePath: '/',
          sidebarPath: './sidebars.js',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Bhashanthara',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Docs',
        },
        {
          href: 'https://github.com/DishanRajapaksha/egeyuma-bhashanthara',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Project',
          items: [
            {
              label: 'Repository',
              href: 'https://github.com/DishanRajapaksha/egeyuma-bhashanthara',
            },
            {
              label: 'Egeyuma',
              href: 'https://github.com/DishanRajapaksha/egeyuma',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Dishan Rajapaksha.`,
    },
  },
};

module.exports = config;
