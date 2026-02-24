import { createHash } from 'node:crypto';
import { describe, expect, it } from 'vitest';

import {
  type SkillTemplate,
  getApplyChangeSkillTemplate,
  getArchiveChangeSkillTemplate,
  getBulkArchiveChangeSkillTemplate,
  getContinueChangeSkillTemplate,
  getExploreSkillTemplate,
  getFeedbackSkillTemplate,
  getFfChangeSkillTemplate,
  getNewChangeSkillTemplate,
  getOnboardSkillTemplate,
  getOpsxApplyCommandTemplate,
  getOpsxArchiveCommandTemplate,
  getOpsxBulkArchiveCommandTemplate,
  getOpsxContinueCommandTemplate,
  getOpsxExploreCommandTemplate,
  getOpsxFfCommandTemplate,
  getOpsxNewCommandTemplate,
  getOpsxOnboardCommandTemplate,
  getOpsxSyncCommandTemplate,
  getOpsxProposeCommandTemplate,
  getOpsxProposeSkillTemplate,
  getOpsxVerifyCommandTemplate,
  getSyncSpecsSkillTemplate,
  getVerifyChangeSkillTemplate,
} from '../../../src/core/templates/skill-templates.js';
import { generateSkillContent } from '../../../src/core/shared/skill-generation.js';

const EXPECTED_FUNCTION_HASHES: Record<string, string> = {
  getExploreSkillTemplate: '000aebcfc65a2fbbdd8bbdef8393c8639a91f792c38ee25d69d9a7b18e216973',
  getNewChangeSkillTemplate: '327f1c7ae72c05dfd837c54e1c3ce36b00a3b6020cb26f6a211946940b9be681',
  getContinueChangeSkillTemplate: 'c056c73034766fedc089aecd65e20592fda8851672cf6d1384c50b0ed6e0ca78',
  getApplyChangeSkillTemplate: '2b8c7b73be2af73ab36adf75ebed3b7e079bfaed3bf6fbcf9851a21fc94614b4',
  getFfChangeSkillTemplate: '1e71174ff33e85ad11f52e7150ebfec83b262d10822a9ab84768b3c96a2de4da',
  getSyncSpecsSkillTemplate: '707794efab4961dc16799b3d656a7d8e4b6dfc9fa97132e0040bdf997149d0b9',
  getOnboardSkillTemplate: 'ca1e45b410889a1ccf8f30878d15e8b5420ca51f3d014e7deb604a4847b49b2a',
  getOpsxExploreCommandTemplate: 'a9d26166bdfd477b55144d52ad6ef9daf837b8ad6c39a11aff17b94ac9fa450c',
  getOpsxNewCommandTemplate: 'fa3e8f585d580e94cbb8db9ea432a4a04b3edf60e599fa3ead67e0665c0d0d45',
  getOpsxContinueCommandTemplate: '67b14f4497d6757a640cf1029b47e11ab6d0e70bba8b41cd8b923b2591be67cf',
  getOpsxApplyCommandTemplate: '2ee19ac60bb456f9027581c0219c9d9912f64cee7467148431589a26d27834e5',
  getOpsxFfCommandTemplate: 'dc789244dc9091403785c5f2aead973e5ff4fcbb471d9f58bfa3cc01ce04d1eb',
  getArchiveChangeSkillTemplate: 'e45be29fdc21c85594a6abf09b89ebd35224a540e9c365dba2a5a11807006db7',
  getBulkArchiveChangeSkillTemplate: '0ce1225b0d48d8feedf1c6abe9271e8fc6cdc19399eef1555b1fcee94507a024',
  getOpsxSyncCommandTemplate: '3de45a6729fc366951185acff71a259e3b3685548f9a4869b0c6207868aff1ca',
  getVerifyChangeSkillTemplate: '5886330f02e282a801d20785c20bce279025e8b802dd76b6dd1e5fe6b5ab624e',
  getOpsxArchiveCommandTemplate: '12032ce250554a7f163eaffae87e0e947f7d356b734863889e7c467cf8bc4b7f',
  getOpsxOnboardCommandTemplate: '4da72eb23f4ebab77b49febc684c120e6b2b9b0f94ac5e82124a387a498d12e9',
  getOpsxBulkArchiveCommandTemplate: '2517f3d5d303fed4f3b670d17eb95428bc7009f8038bdaf4d803c38206997236',
  getOpsxVerifyCommandTemplate: '65dca361c7a978ccdf810150e1ff7a07f805fdf1f56c3f6c75e8a62f476fec43',
  getOpsxProposeSkillTemplate: 'aa56fe409372067d87cafa57d9f4d8761c899930740b41a1bea5b2c116e63421',
  getOpsxProposeCommandTemplate: '89ff711660ad150694cd30730e663ba1c001d21e0f931c8f01bcfe4125c2273c',
  getFeedbackSkillTemplate: 'bf8c061e31c8a6e5735f812bfbf5165b3c5e96efe108b8aa37dbcc1fa3a3fc66',
};

const EXPECTED_GENERATED_SKILL_CONTENT_HASHES: Record<string, string> = {
  'openspec-hw2-explore': 'c5e06ffa7880c7285cb0bae0f0e4fa944aa564b8128fd0aaf7668c67f5d10c16',
  'openspec-hw2-new-change': '78840ae37fba23c024383794e6c2e9bfa2411e1df9b279a9643aae00a02ab8dd',
  'openspec-hw2-continue-change': 'e4cf4c1be5da42069b25540df90e6d37f83e15afdea15a069dea52cb6b93a0cc',
  'openspec-hw2-apply-change': '4a62ac634e6b04088251eccf26a6fd9f95b7d12da5f8275fa76c225dea818841',
  'openspec-hw2-ff-change': '0d36e94f0290a54499a49cfb7478d5f30dc2d7aa65d32181154fae86f6e5c954',
  'openspec-hw2-sync-specs': '8399bd41381e98b6a597838acf1c43726a663933f278056069fda2e8520571cc',
  'openspec-hw2-archive-change': 'a90aaa919beb45862f41996707599df086b11354a7a7f0d1c7b5b5ce7f44b665',
  'openspec-hw2-bulk-archive-change': '67968dcd451204aa0c140089150486c783cad5b50b22a9de461860e9db92b753',
  'openspec-hw2-verify-change': '493f2889da84d1d1e9d20f5a238efe8dbd84c391c072b82038bad608b99e85d7',
  'openspec-hw2-onboard': 'b61fe476713d8576b3ac2f1e05dd8b1ef4c6c7a74c7faabf58a48f31f40797dc',
  'openspec-hw2-propose': 'd6e99621798b0710cd388d320d85e5f3cf26718b38246a27780260f9bd9714b9',
};

function stableStringify(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map(stableStringify).join(',')}]`;
  }

  if (value && typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, item]) => `${JSON.stringify(key)}:${stableStringify(item)}`);

    return `{${entries.join(',')}}`;
  }

  return JSON.stringify(value);
}

function hash(value: string): string {
  return createHash('sha256').update(value).digest('hex');
}

describe('skill templates split parity', () => {
  it('preserves all template function payloads exactly', () => {
    const functionFactories: Record<string, () => unknown> = {
      getExploreSkillTemplate,
      getNewChangeSkillTemplate,
      getContinueChangeSkillTemplate,
      getApplyChangeSkillTemplate,
      getFfChangeSkillTemplate,
      getSyncSpecsSkillTemplate,
      getOnboardSkillTemplate,
      getOpsxExploreCommandTemplate,
      getOpsxNewCommandTemplate,
      getOpsxContinueCommandTemplate,
      getOpsxApplyCommandTemplate,
      getOpsxFfCommandTemplate,
      getArchiveChangeSkillTemplate,
      getBulkArchiveChangeSkillTemplate,
      getOpsxSyncCommandTemplate,
      getVerifyChangeSkillTemplate,
      getOpsxArchiveCommandTemplate,
      getOpsxOnboardCommandTemplate,
      getOpsxBulkArchiveCommandTemplate,
      getOpsxVerifyCommandTemplate,
      getOpsxProposeSkillTemplate,
      getOpsxProposeCommandTemplate,
      getFeedbackSkillTemplate,
    };

    const actualHashes = Object.fromEntries(
      Object.entries(functionFactories).map(([name, fn]) => [name, hash(stableStringify(fn()))])
    );

    expect(actualHashes).toEqual(EXPECTED_FUNCTION_HASHES);
  });

  it('preserves generated skill file content exactly', () => {
    // Intentionally excludes getFeedbackSkillTemplate: skillFactories only models templates
    // deployed via generateSkillContent, while feedback is covered in function payload parity.
    const skillFactories: Array<[string, () => SkillTemplate]> = [
      ['openspec-hw2-explore', getExploreSkillTemplate],
      ['openspec-hw2-new-change', getNewChangeSkillTemplate],
      ['openspec-hw2-continue-change', getContinueChangeSkillTemplate],
      ['openspec-hw2-apply-change', getApplyChangeSkillTemplate],
      ['openspec-hw2-ff-change', getFfChangeSkillTemplate],
      ['openspec-hw2-sync-specs', getSyncSpecsSkillTemplate],
      ['openspec-hw2-archive-change', getArchiveChangeSkillTemplate],
      ['openspec-hw2-bulk-archive-change', getBulkArchiveChangeSkillTemplate],
      ['openspec-hw2-verify-change', getVerifyChangeSkillTemplate],
      ['openspec-hw2-onboard', getOnboardSkillTemplate],
      ['openspec-hw2-propose', getOpsxProposeSkillTemplate],
    ];

    const actualHashes = Object.fromEntries(
      skillFactories.map(([dirName, createTemplate]) => [
        dirName,
        hash(generateSkillContent(createTemplate(), 'PARITY-BASELINE')),
      ])
    );

    expect(actualHashes).toEqual(EXPECTED_GENERATED_SKILL_CONTENT_HASHES);
  });
});
