import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from 'react-router-dom';
import { getDuplicatedWords, mergeDuplicatedWords } from '../../api/api';

import {
  Table,
  Panel,
  PanelGroup,
  Tag,
  TagGroup,
  FlexboxGrid,
  Input,
  InputGroup,
  IconButton,
  Button,
  ButtonGroup,
  Message,
  Placeholder,
  Drawer,
  SelectPicker,
  Badge,
  Divider,
  Tooltip,
  Whisper,
  Pagination,
  Checkbox,
  Modal,
  Form,
  toaster
} from "rsuite";
import SearchIcon from "@rsuite/icons/Search";
import InfoOutlineIcon from "@rsuite/icons/InfoOutline";
import EyeIcon from "@rsuite/icons/legacy/Eye";
import ReloadIcon from "@rsuite/icons/Reload";
import MergeIcon from "@rsuite/icons/legacy/Exchange";

const { Column, HeaderCell, Cell } = Table;

/**
 * Utility: parse a root label like "下さる (ID: 12bf2...)" into { word, id }
 */
function parseRootLabel(label) {
  if (!label) return { word: label, id: null };
  const m = label.match(/^(.*)\s*\(ID:\s*([^\)]+)\)/);
  if (!m) return { word: label, id: null };
  return { word: m[1], id: m[2] };
}

/**
 * Utility: normalize backend payload into an array of roots
 * Input shape:
 * {
 *   "<rootLabel>": [ {id, root_word_id, word, ...}, ... ],
 *   ...
 * }
 */
function normalize(duplicatedWordsObj) {
  if (!duplicatedWordsObj || typeof duplicatedWordsObj !== "object") return [];
  return Object.entries(duplicatedWordsObj).map(([label, items]) => {
    const { word: rootWord, id: rootId } = parseRootLabel(label);
    return {
      label,
      rootWord,
      rootId,
      count: Array.isArray(items) ? items.length : 0,
      items: Array.isArray(items) ? items : []
    };
  });
}

/**
 * Branch table component for a single root
 */
function BranchesTable({ items, onMerge }) {
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [query, setQuery] = useState("");
  const [levelFilter, setLevelFilter] = useState(null);
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [showMergeModal, setShowMergeModal] = useState(false);
  const [mergeFormData, setMergeFormData] = useState({});
  const [mergeLoading, setMergeLoading] = useState(false);
  const [mergeError, setMergeError] = useState(null);

  const levelOptions = useMemo(() => {
    const set = new Set(items?.map(i => i.level).filter(Boolean));
    return Array.from(set).sort().map(v => ({ label: v, value: v }));
  }, [items]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return (items || []).filter(row => {
      const passQuery = !q
        || (row.word && row.word.toLowerCase().includes(q))
        || (row.jp_pronunciation && row.jp_pronunciation.toLowerCase().includes(q))
        || (row.kr_meaning && row.kr_meaning.toLowerCase().includes(q));
      const passLevel = !levelFilter || row.level === levelFilter;
      return passQuery && passLevel;
    });
  }, [items, query, levelFilter]);

  const total = filtered.length;
  const paged = useMemo(() => {
    const start = (page - 1) * limit;
    return filtered.slice(start, start + limit);
  }, [filtered, page, limit]);

  useEffect(() => {
    // Reset to first page on filter change
    setPage(1);
  }, [query, levelFilter, limit]);

  // 선택된 항목이 변경될 때마다 병합 폼 데이터 업데이트
  useEffect(() => {
    if (selectedItems.size > 0) {
      const selectedItemsArray = Array.from(selectedItems);
      const firstItem = items.find(item => item.id === selectedItemsArray[0]);
      if (firstItem) {
        setMergeFormData({
          word: firstItem.word || "",
          jp_pronunciation: firstItem.jp_pronunciation || "",
          kr_pronunciation: firstItem.kr_pronunciation || "",
          kr_meaning: firstItem.kr_meaning || "",
          level: firstItem.level || ""
        });
      }
    }
  }, [selectedItems, items]);

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedItems(new Set(paged.map(item => item.id)));
    } else {
      setSelectedItems(new Set());
    }
  };

  const handleSelectItem = (itemId, checked) => {
    const newSelected = new Set(selectedItems);
    if (checked) {
      newSelected.add(itemId);
    } else {
      newSelected.delete(itemId);
    }
    setSelectedItems(newSelected);
  };

  const handleMerge = async () => {
    if (selectedItems.size < 2) {
      setMergeError("병합하려면 최소 2개 이상의 항목을 선택해야 합니다.");
      return;
    }

    setMergeLoading(true);
    setMergeError(null);

    try {
      const selectedItemsArray = Array.from(selectedItems);
      
      // API 호출 전에 모달을 닫아서 렌더링 문제 방지
      setShowMergeModal(false);
      
      const result = await mergeDuplicatedWords(selectedItemsArray, mergeFormData);
      
      if (result.data.success) {
        // 성공 시 선택 초기화
        setSelectedItems(new Set());
        // 부모 컴포넌트에 병합 완료 알림
        if (onMerge) {
          onMerge();
        }
      }
    } catch (error) {
      console.error('Merge error:', error);
      setMergeError(error.response?.data?.detail || error.message || "병합 중 오류가 발생했습니다.");
      // 오류 발생 시 모달 다시 열기
      setShowMergeModal(true);
    } finally {
      setMergeLoading(false);
      setShowMergeModal(false);
    }
  };

  const selectedCount = selectedItems.size;

  return (
    <Panel bordered bodyFill>
      <div className="p-3">
        <FlexboxGrid align="middle" justify="space-between">
          <FlexboxGrid.Item colspan={14}>
            <InputGroup inside style={{ maxWidth: 420 }}>
              <Input
                placeholder="검색: 단어 / 읽기 / 뜻"
                value={query}
                onChange={setQuery}
              />
              <InputGroup.Addon>
                <SearchIcon />
              </InputGroup.Addon>
            </InputGroup>
          </FlexboxGrid.Item>
          <FlexboxGrid.Item colspan={10}>
            <div style={{ display: "flex", gap: 12, justifyContent: "flex-end" }}>
              {selectedCount > 0 && (
                <Button
                  appearance="primary"
                  startIcon={<MergeIcon />}
                  onClick={() => setShowMergeModal(true)}
                  disabled={selectedCount < 2}
                >
                  병합 ({selectedCount})
                </Button>
              )}
              <SelectPicker
                data={levelOptions}
                placeholder="Level 필터"
                value={levelFilter}
                onChange={setLevelFilter}
                searchable={false}
                style={{ width: 160 }}
                cleanable
              />
              <SelectPicker
                data={[10, 20, 50, 100].map(n => ({ label: `${n}/page`, value: n }))}
                value={limit}
                onChange={setLimit}
                searchable={false}
                style={{ width: 120 }}
              />
            </div>
          </FlexboxGrid.Item>
        </FlexboxGrid>
      </div>

      <Table data={paged} height={360} wordWrap>
        <Column width={50} align="center">
          <HeaderCell>
            <Checkbox
              checked={selectedCount === paged.length && paged.length > 0}
              indeterminate={selectedCount > 0 && selectedCount < paged.length}
              onChange={(value, checked) => handleSelectAll(checked)}
            />
          </HeaderCell>
          <Cell>
            {row => (
              <Checkbox
                checked={selectedItems.has(row.id)}
                onChange={(value, checked) => handleSelectItem(row.id, checked)}
              />
            )}
          </Cell>
        </Column>
        <Column flexGrow={1} minWidth={180}>
          <HeaderCell>단어</HeaderCell>
          <Cell dataKey="word" />
        </Column>
        <Column flexGrow={1} minWidth={180}>
          <HeaderCell>사용자</HeaderCell>
          <Cell dataKey="user_name" />
        </Column>
        <Column width={140}>
          <HeaderCell>읽기(JP)</HeaderCell>
          <Cell dataKey="jp_pronunciation" />
        </Column>
        <Column width={120}>
          <HeaderCell>수준</HeaderCell>
          <Cell>{row => <Tag>{row.level || "-"}</Tag>}</Cell>
        </Column>
        <Column flexGrow={2} minWidth={240}>
          <HeaderCell>한국어 뜻</HeaderCell>
          <Cell dataKey="kr_meaning" />
        </Column>
        <Column width={220}>
          <HeaderCell>생성 시각</HeaderCell>
          <Cell>{row => row.created_at?.replace("T", " ").replace("+00:00", "Z") || "-"}</Cell>
        </Column>
        <Column width={220}>
          <HeaderCell>수정 시각</HeaderCell>
          <Cell>{row => row.updated_at?.replace("T", " ").replace("+00:00", "Z") || "-"}</Cell>
        </Column>
      </Table>

      <div className="px-3 py-2" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span>총 <b>{total}</b>개</span>
        <Pagination
          total={total}
          limit={limit}
          activePage={page}
          onChangePage={setPage}
          prev
          next
          first
          last
          layout={["total", "pager", "limit"]}
          limitOptions={[10, 20, 50, 100]}
        />
      </div>

      {/* 병합 모달 */}
      <Modal 
        open={showMergeModal} 
        onClose={() => {
          setShowMergeModal(false);
          setMergeError(null);
        }} 
        size="md"
      >
        <Modal.Header>
          <Modal.Title>중복 단어 병합</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="mb-3">
            <Message type="info" showIcon>
              선택된 <b>{selectedCount}개</b>의 단어를 하나로 병합합니다.
              아래 정보는 병합된 새 단어의 정보가 됩니다.
            </Message>
          </div>
          
          {mergeError && (
            <div className="mb-3">
              <Message type="error" showIcon>
                {mergeError}
              </Message>
            </div>
          )}

          <Form fluid>
            <Form.Group>
              <Form.ControlLabel>단어</Form.ControlLabel>
              <Form.Control
                name="word"
                value={mergeFormData.word || ""}
                onChange={(value) => setMergeFormData(prev => ({ ...prev, word: value }))}
                placeholder="일본어 단어"
              />
            </Form.Group>
            
            <Form.Group>
              <Form.ControlLabel>일본어 읽기</Form.ControlLabel>
              <Form.Control
                name="jp_pronunciation"
                value={mergeFormData.jp_pronunciation || ""}
                onChange={(value) => setMergeFormData(prev => ({ ...prev, jp_pronunciation: value }))}
                placeholder="히라가나/카타카나"
              />
            </Form.Group>
            
            <Form.Group>
              <Form.ControlLabel>한국어 읽기</Form.ControlLabel>
              <Form.Control
                name="kr_pronunciation"
                value={mergeFormData.kr_pronunciation || ""}
                onChange={(value) => setMergeFormData(prev => ({ ...prev, kr_pronunciation: value }))}
                placeholder="한국어 발음"
              />
            </Form.Group>
            
            <Form.Group>
              <Form.ControlLabel>한국어 뜻</Form.ControlLabel>
              <Form.Control
                name="kr_meaning"
                value={mergeFormData.kr_meaning || ""}
                onChange={(value) => setMergeFormData(prev => ({ ...prev, kr_meaning: value }))}
                placeholder="한국어 의미"
              />
            </Form.Group>
            
            <Form.Group>
              <Form.ControlLabel>수준</Form.ControlLabel>
              <Form.Control
                name="level"
                value={mergeFormData.level || ""}
                onChange={(value) => setMergeFormData(prev => ({ ...prev, level: value }))}
                placeholder="N5, N4, N3, N2, N1"
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={() => {
            setShowMergeModal(false);
            setMergeError(null);
          }} appearance="subtle">
            취소
          </Button>
          <Button
            appearance="primary"
            onClick={handleMerge}
            loading={mergeLoading}
            disabled={!mergeFormData.word || !mergeFormData.jp_pronunciation || !mergeFormData.kr_meaning || !mergeFormData.level}
          >
            병합 실행
          </Button>
        </Modal.Footer>
      </Modal>
    </Panel>
  );
}

/**
 * Main page component
 * Props:
 *   - duplicatedWords: optional object delivered from backend
 *   - endpoint: optional string to fetch from (GET)
 */
export default function DuplicatedWords() {
  const [dataObj, setDataObj] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedRoot, setSelectedRoot] = useState(null);
  const [query, setQuery] = useState("");

  // Fetch from backend if prop not supplied
  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getDuplicatedWords();
      const json = res.data;
      setDataObj(json);
    } catch (e) {
      setError(e.message || "로드 실패");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let ignore = false;
    async function load() {
      await loadData();
    }
    load();
    return () => { ignore = true; };
  }, []);

  // 병합 완료 후 데이터 새로고침
  const handleMergeComplete = () => {
    loadData();
    setSelectedRoot(null);
  };

  const roots = useMemo(() => normalize(dataObj), [dataObj]);

  const filteredRoots = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return roots;
    return roots.filter(r =>
      (r.rootWord && r.rootWord.toLowerCase().includes(q)) ||
      (r.rootId && r.rootId.toLowerCase().includes(q))
    );
  }, [roots, query]);

  const stats = useMemo(() => {
    const totalRoots = roots.length;
    const totalBranches = roots.reduce((acc, r) => acc + (r.count || 0), 0);
    return { totalRoots, totalBranches };
  }, [roots]);

  const RootInfoCell = ({ rowData, ...props }) => (
    <Cell {...props}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <Badge content={rowData.count} style={{ background: undefined }}>
          <Tag size="lg">{rowData.rootWord || rowData.label}</Tag>
        </Badge>
        {rowData.rootId && (
          <Tag size="sm" appearance="ghost">{rowData.rootId}</Tag>
        )}
      </div>
    </Cell>
  );

  return (
    <div style={{ padding: 16 }}>
      <FlexboxGrid justify="space-between" align="middle" className="mb-3">
        <FlexboxGrid.Item colspan={14}>
          <h3 style={{ margin: 0 }}>중복/파생 단어 그룹 뷰어</h3>
          <div style={{ color: "var(--rs-text-secondary)", marginTop: 4 }}>
            루트별로 연결된 단어(브랜치)를 묶어 보여줍니다.
          </div>
        </FlexboxGrid.Item>
        <FlexboxGrid.Item colspan={10} style={{ display: "flex", gap: 12, justifyContent: "flex-end" }}>
          <InputGroup inside style={{ width: 320 }}>
            <Input placeholder="루트 단어/ID 검색" value={query} onChange={setQuery} />
            <InputGroup.Addon><SearchIcon /></InputGroup.Addon>
          </InputGroup>
        </FlexboxGrid.Item>
      </FlexboxGrid>

      <Panel bordered>
        <FlexboxGrid align="middle" justify="space-around" style={{ gap: 12 }}>
          <StatCard label="루트 개수" value={stats.totalRoots} />
          <StatCard label="브랜치 총합" value={stats.totalBranches} />
        </FlexboxGrid>
      </Panel>

      <Divider />

      {loading && (
        <Placeholder.Grid rows={6} columns={6} active />
      )}
      {error && (
        <Message type="error" showIcon>
          데이터를 불러오지 못했습니다: {String(error)}
        </Message>
      )}

      {!loading && !error && (
        <Panel bordered bodyFill>
          <Table data={filteredRoots} height={500} wordWrap rowHeight={56} onRowClick={row => setSelectedRoot(row)}>
            <Column flexGrow={2} minWidth={260}>
              <HeaderCell>루트</HeaderCell>
              <RootInfoCell dataKey="label" />
            </Column>
            <Column width={120} align="center">
              <HeaderCell>브랜치 수</HeaderCell>
              <Cell dataKey="count" />
            </Column>
            <Column flexGrow={1} minWidth={140} align="center">
              <HeaderCell>열기</HeaderCell>
              <Cell>
                {row => (
                  <Button appearance="primary" size="sm" startIcon={<EyeIcon />} onClick={() => setSelectedRoot(row)}>
                    상세
                  </Button>
                )}
              </Cell>
            </Column>
          </Table>
        </Panel>
      )}

      <Drawer open={!!selectedRoot} onClose={() => setSelectedRoot(null)} size="full">
        <Drawer.Header>
          <Drawer.Title>
            {selectedRoot ? (
              <span>
                루트: <b>{selectedRoot.rootWord}</b>{" "}
                {selectedRoot.rootId && <Tag appearance="ghost">{selectedRoot.rootId}</Tag>}
              </span>
            ) : "상세"}
          </Drawer.Title>
          <Drawer.Actions>
            <Button onClick={() => setSelectedRoot(null)} appearance="primary">닫기</Button>
          </Drawer.Actions>
        </Drawer.Header>
        <Drawer.Body>
          {selectedRoot && (
            <BranchesTable 
              items={selectedRoot.items} 
              onMerge={handleMergeComplete}
            />
          )}
        </Drawer.Body>
      </Drawer>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <Panel bordered style={{ minWidth: 220, flex: 1 }}>
      <div style={{ padding: 12 }}>
        <div style={{ color: "var(--rs-text-secondary)", marginBottom: 6 }}>{label}</div>
        <div style={{ fontSize: 28, fontWeight: 700 }}>{value}</div>
      </div>
    </Panel>
  );
}
