// @ts-check

const sidebars = {
  docs: [
    'intro',
    'quickstart',
    'concepts',
    {
      type: 'category',
      label: 'Datasets',
      items: [
        'dataset-commands',
        'fetch-mmlu',
        'arc-converter',
        'commonsenseqa-converter',
        'labelled-choice-converters',
      ],
    },
    {
      type: 'category',
      label: 'Translation workflow',
      items: [
        'translation-commands',
        'resume-retry',
        'auto-manifest-and-pilot',
        'run-manifest',
      ],
    },
    {
      type: 'category',
      label: 'Review and export',
      items: [
        'quality-review',
        'labelstudio-repair',
        'egeyuma-export',
      ],
    },
    'development',
  ],
};

module.exports = sidebars;
